package com.example.duplicate.TCPclient;

import android.util.Log;

import com.example.duplicate.data.LoginDataSource;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.Socket;

public class TCPClient {

    private String host;
    private String port;
    private String emailOrPhone;
    private String password;

    private String Result;

    private Socket socket;

    private String[] pMessage;
    private String recvMessage;


    public TCPClient(String emailOrPhone,String password){
        this.emailOrPhone=emailOrPhone;
        this.password=password;
        InitClient();
    }

    private void InitClient(){
        host= "49.234.110.208";
        port= "9998";
        Result = "Unknown";
    }

    public String[] get_history(){
        fetchHistory();
        return pMessage;
    }

    public void ConnectToServer() {
        startNetThread();
    }

    public String getResult() {return Result;}

    public String getRecvMessage() {return recvMessage;}

    public void closeSocket() {
        try{this.socket.close();} catch (Exception e){e.printStackTrace();}
    }
    public void sendMessage(final String msg){
        Thread t3 =new Thread(){
            @Override
            public void run(){
                OutputStream out;
                if (socket!=null){
                    try {
                        out = socket.getOutputStream();
                        out.write(("1|"+msg).getBytes());
                        out.flush();
                    }catch (Exception e){
                        e.printStackTrace();
                    }
                }
            }
        };
        t3.start();
    }

    public void sendQuit(){
        Thread t4=new Thread(){
            @Override
            public void run(){
                OutputStream out;
                if (socket!=null){
                    try {
                        out = socket.getOutputStream();
                        out.write(("-1|quit").getBytes());
                        out.flush();
                        closeSocket();
                    }catch (Exception e){
                        e.printStackTrace();
                    }
                }
            }
        };
        t4.start();
    }

    public void fetchHistory(){
        Thread t3 = new Thread(){
            @Override
            public void run() {
                InputStream is;
                if(socket!=null) {
                   try {
                       is = socket.getInputStream();
                       byte[] bytes = new byte[1024];
                       int n = is.read(bytes);
                       String historyMessage = new String(bytes, 0, n);
                       historyMessage = historyMessage.substring(0,historyMessage.length()-1);
                       pMessage = historyMessage.split("\\| ");
                   }catch (Exception e){
                       e.printStackTrace();
                   }
                }
            }
        };
        t3.start();
        try{
            t3.join();
        }catch (InterruptedException e){
            e.printStackTrace();
        }
    }

    public void startRecvMessage(){
        Thread t2 =new Thread(){
            @Override
            public void run(){
                InputStream is;
                while (socket!=null){
                    try {
                        is = socket.getInputStream();
                        byte[] bytes = new byte[1024];
                        int n = is.read(bytes);
                        recvMessage = new String(bytes, 0, n);
                    }catch (Exception e){
                        e.printStackTrace();
                    }
                }
            }
        };
        t2.start();

    }

    private void startNetThread() {
        Thread t1 = new Thread() {
            @Override
            public void run() {
                try {
                    socket = new Socket(host, Integer.parseInt(port));
                    System.out.println("connect to server.");
                    OutputStream outputStream = socket.getOutputStream();
                    outputStream.write(("login").getBytes());
                    outputStream.flush();
                    System.out.println(socket);
                    Result = "success";
//                    InputStream is = socket.getInputStream();
//                    byte[] bytes = new byte[1024];
//                    int n = is.read(bytes);
//                    String msg = new String(bytes, 0, n);
//                    System.out.println(msg);
////                    Message msg = handler.obtainMessage(HANDLER_MSG_TELL_RECV, new String(bytes, 0, n));
//////                    msg.sendToTarget();
//                    if(msg.equals("success")){
//                        Result = "success";
//                    }else if(msg.equals("exit")){
//                        Log.d("LoginActivity","exit.");
//                        is.close();
//                        socket.close();
//                        Result = "服务器没有空闲线程，请稍后重试";
//                    }else{
//                        Result= msg;
//                    }
                    //is.close();
                    //socket.close();
                } catch (Exception e) {
                    e.printStackTrace();
//                    Log.d("LoginActivity","Wrong.");
                    Result = "登录失败";
                }
            }
        };
        t1.start();//暂停其他活动
//        try{
//             t1.join();
//        }catch (InterruptedException e){
//            e.printStackTrace();
//        }
//
    }
}
