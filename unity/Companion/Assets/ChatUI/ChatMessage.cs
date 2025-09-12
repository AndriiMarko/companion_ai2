using System;

[Serializable]   // Needed so Unity can save it in JSON
public class ChatMessage
{
    public string text;
    public bool isSentByUser;
    public string timestamp;
}
