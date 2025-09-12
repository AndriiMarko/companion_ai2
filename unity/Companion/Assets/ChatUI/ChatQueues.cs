using System.Collections.Generic;

public static class ChatQueues
{
    private static readonly object sendLock = new object();
    private static readonly object receiveLock = new object();

    private static readonly Queue<string> sendQueue = new Queue<string>();
    private static readonly Queue<string> receiveQueue = new Queue<string>();

    public static void EnqueueSend(string msg)
    {
        lock (sendLock)
        {
            sendQueue.Enqueue(msg);
        }
    }

    public static bool TryDequeueSend(out string msg)
    {
        lock (sendLock)
        {
            if (sendQueue.Count > 0)
            {
                msg = sendQueue.Dequeue();
                return true;
            }
        }
        msg = null;
        return false;
    }

    public static void EnqueueReceive(string msg)
    {
        lock (receiveLock)
        {
            receiveQueue.Enqueue(msg);
        }
    }

    public static bool TryDequeueReceive(out string msg)
    {
        lock (receiveLock)
        {
            if (receiveQueue.Count > 0)
            {
                msg = receiveQueue.Dequeue();
                return true;
            }
        }
        msg = null;
        return false;
    }
}
