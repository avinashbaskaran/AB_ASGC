#include <iostream>
#include <string>
#include <WS2tcpip.h>
#pragma comment (lib, "ws2_32.lib")

using namespace std;

void main(){
    //Target host details:
    string HOST = "131.204.24.126"; // Delsys Trigno server address

    #define CMD_PORT 50040          // Trigno command port
    #define HF_DATA_PORT 50041      // Trigno high frequency data port
    #define LF_DATA_PORT 50042      // Trigno low frequency data port
    #define IM_EMG_DATA_PORT 50043  // Trigno IM EMG data port
    #define IM_AUX_DATA_PORT 50044  // Trigno IM Aux data port

    // Initialize WinSock
    WSAData data;
    WORD ver = MAKEWORD(2,2);
    int wsResult = WSAStartup(ver, &data);
    if (wsResult != 0)
    {
        cerr << "can't start Winsock, Err #" << wsResult << endl;
        return; 
    }

    // Create socket 
    SOCKET sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == INVALID_SOCKET)
    { 
        cerr << "Can't create socket, Err #" << WSAGetLastError() << endl;
        WSACleanup();
        return;
    } 
    
    // Fill in a hint structure
    sockaddr_in hint;
    hint.sin_family = AF_INET;
    hint.sin_port = htons(CMD_PORT);
    inet_pton(AF_INET, HOST.c_str(), &hint.sin_addr);

    // Connect to a server
    int connResult = connect(sock, (sockaddr*)&hint, sizeof(hint));
    if (connResult == SOCKET_ERROR)
    {
        cerr << "can't connect to server, Err #" << WSAGetLastError() << endl;
        closesocket(sock);
        WSACleanup();
        return;
    }
    
    // Do-while loop to send and receive data
    char buf[4096];
    string  userInput;
    
        // Prompt the user for some text    
    while (userInput.size()<5)
    {
        cout << ">";
        getline(cin,userInput);
    }
    int sendResult = send(sock, userInput.c_str(), userInput.size() + 1, 0);
    if(sendResult != SOCKET_ERROR)
    {
        // Wait for response
        ZeroMemory(buf,4096);
        int bytesReceived = recv(sock, buf, 4096,0);
        if (bytesReceived>0)
        {
            // Echo response to console
            cout << "SERVER>" << string(buf,0,bytesReceived) << endl;
        }
    }

    // Close everything down
    closesocket(sock);
    WSACleanup();
}

