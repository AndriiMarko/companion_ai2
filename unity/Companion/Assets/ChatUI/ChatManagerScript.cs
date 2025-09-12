using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using UnityEngine;
using UnityEngine.UI;
using TMPro;


public class ChatManager : MonoBehaviour
{
    [Header("UI References")]
    public Transform messageContainer;
    public GameObject messageBubbleLeft;   // Received
    public GameObject messageBubbleRight;  // Sent
    public TMP_InputField inputField;
    public Button sendButton;
    public ScrollRect scrollRect;

    private List<ChatMessage> chatHistory = new List<ChatMessage>();
    //private string savePath = Application.persistentDataPath;

    private SocketClient socketClient;

    void Start()
    {
        sendButton.onClick.AddListener(OnSendButtonClicked);

        // Start socket client in background
        var socketClient = new SocketClient("127.0.0.1", 55555, "63de4c03-1216-477a-8765-dc32a618974d", "Clara");
        socketClient.Start(); 

        //LoadChat();
    }

    private void OnSendButtonClicked()
    {
        string userInput = inputField.text;
        if (string.IsNullOrWhiteSpace(userInput)) return;

        AddMessage(userInput, true); // true = user message
        inputField.text = "";

        // Push into send queue
        ChatQueues.EnqueueSend(userInput);
    }
    
    void Update()
    {
        // Check receive queue
        while (ChatQueues.TryDequeueReceive(out string msg))
        {
            AddMessage(msg, false);
        }
    }

    public void AddMessage(string message, bool isSentByUser)
    {
        // Create bubble
        GameObject bubble = Instantiate(
            isSentByUser ? messageBubbleRight : messageBubbleLeft,
            messageContainer
        );
        TMP_Text bubbleText = bubble.GetComponentInChildren<TMP_Text>();
        bubbleText.text = message;

        // Add to history
        chatHistory.Add(new ChatMessage
        {
            text = message,
            isSentByUser = isSentByUser,
            timestamp = DateTime.Now.ToString("HH:mm")
        });

        //SaveChat();

        // Scroll to bottom
        Canvas.ForceUpdateCanvases();
        scrollRect.verticalNormalizedPosition = 0f;
    }

    /*private void SaveChat()
    {
        string json = JsonUtility.ToJson(new ChatWrapper { messages = chatHistory }, true);
        File.WriteAllText(savePath, json);
    }

    private void LoadChat()
    {
        if (!File.Exists(savePath)) return;

        string json = File.ReadAllText(savePath);
        ChatWrapper wrapper = JsonUtility.FromJson<ChatWrapper>(json);

        if (wrapper != null && wrapper.messages != null)
        {
            chatHistory = wrapper.messages;

            foreach (ChatMessage msg in chatHistory)
            {
                GameObject bubble = Instantiate(
                    msg.isSentByUser ? messageBubbleRight : messageBubbleLeft,
                    messageContainer
                );
                TMP_Text bubbleText = bubble.GetComponentInChildren<TMP_Text>();
                bubbleText.text = $"{msg.text}"; // You can also add timestamp here
            }

            Canvas.ForceUpdateCanvases();
            scrollRect.verticalNormalizedPosition = 0f;
        }
    }*/

    void OnDestroy()
    {
        socketClient?.Close();
    }

    void OnApplicationQuit()
    {
        socketClient?.Close();
    }

    [Serializable]
    private class ChatWrapper
    {
        public List<ChatMessage> messages;
    }
}
