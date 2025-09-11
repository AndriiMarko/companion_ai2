using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class ChatManager : MonoBehaviour
{
    [Header("UI References")]
    public Transform messageContainer;       // The Content object in ScrollView
    public GameObject messageBubbleLeft;     // Prefab for received messages
    public GameObject messageBubbleRight;    // Prefab for sent messages
    public TMP_InputField inputField;
    public Button sendButton;
    public ScrollRect scrollRect;

    void Start()
    {
        sendButton.onClick.AddListener(SendMessage);
    }

    void SendMessage()
    {
        if (string.IsNullOrWhiteSpace(inputField.text)) return;

        CreateMessage(inputField.text, true);  // true = sent by player
        inputField.text = "";
    }

    public void CreateMessage(string message, bool isSentByUser)
    {
        GameObject bubble = Instantiate(
            isSentByUser ? messageBubbleRight : messageBubbleLeft,
            messageContainer
        );

        TMP_Text bubbleText = bubble.GetComponentInChildren<TMP_Text>();
        bubbleText.text = message;

        // Scroll to bottom after message is added
        Canvas.ForceUpdateCanvases();
        scrollRect.verticalNormalizedPosition = 0f;
    }
}

