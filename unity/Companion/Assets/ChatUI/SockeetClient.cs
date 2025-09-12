using System;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;

public class SocketClient
{
    private readonly string host;
    private readonly int port;
    private readonly string conversationId;
    private readonly string characterName;

    private TcpClient client;
    private NetworkStream stream;
    private Thread thread;
    private volatile bool running = false;

    public SocketClient(string host, int port, string conversationId, string characterName)
    {
        this.host = host;
        this.port = port;
        this.conversationId = conversationId;
        this.characterName = characterName;
    }

    public void Start()
    {
        running = true;
        thread = new Thread(Run);
        thread.IsBackground = true;
        thread.Start();
    }

    public void Close()
    {
        running = false;

        try
        {
            stream?.Close();
            client?.Close();
        }
        catch (Exception e)
        {
            Debug.LogWarning($"Socket close error: {e.Message}");
        }

        if (thread != null && thread.IsAlive)
        {
            thread.Join(200); // wait briefly for thread to exit
        }
    }

    private void Run()
    {
        try
        {
            Debug.Log("Thread started");
            client = new TcpClient(host, port);
            stream = client.GetStream();

            while (running)
            {
                // 🔹 Send messages
                if (ChatQueues.TryDequeueSend(out string userInput))
                {
                    Debug.Log($"Sending: {userInput}");
                    SCRequest request = new SCRequest();
                    request.input = userInput;
                    request.conversation_id = conversationId;
                    request.character_name = characterName;

                    Debug.Log("Request: " + request);
                    string json = JsonUtility.ToJson(request);
                    Debug.Log("JSON: " + json);
                    byte[] data = Encoding.UTF8.GetBytes(json);
                    byte[] size = BitConverter.GetBytes(data.Length);

                    stream.Write(size, 0, size.Length);
                    stream.Write(data, 0, data.Length);
                }

                // 🔹 Receive messages
                if (stream.DataAvailable)
                {
                    Debug.Log("Data available to read");
                    byte[] rawSize = new byte[4];
                    int read = stream.Read(rawSize, 0, 4);
                    if (read == 0) break;

                    int respSize = BitConverter.ToInt32(rawSize, 0);
                    byte[] respData = new byte[respSize];
                    int received = 0;
                    while (received < respSize)
                    {
                        int chunk = stream.Read(respData, received, respSize - received);
                        if (chunk == 0) break;
                        received += chunk;
                    }

                    string respJson = Encoding.UTF8.GetString(respData);
                    ResponseWrapper response = JsonUtility.FromJson<ResponseWrapper>(respJson);
                    string answer = response.answer ?? "";

                    ChatQueues.EnqueueReceive(answer);
                }

                Thread.Sleep(100); // small delay to avoid busy loop
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"Socket error: {e.Message}");
        }
        finally
        {
            stream?.Close();
            client?.Close();
        }
    }

    [Serializable]
    private class ResponseWrapper
    {
        public string answer;
    }
}
