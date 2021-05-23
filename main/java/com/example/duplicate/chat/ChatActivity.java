package com.example.duplicate.chat;

import android.annotation.SuppressLint;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.Message;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;

import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import java.io.IOException;
import java.sql.Time;
import java.util.ArrayList;
import java.util.List;
import java.util.Timer;

import com.example.duplicate.TCPclient.TCPClient;

import com.example.duplicate.R;
import com.example.duplicate.data.LoginDataSource;
import com.xiasuhuei321.loadingdialog.manager.StyleManager;
import com.xiasuhuei321.loadingdialog.view.LoadingDialog;

public class ChatActivity extends AppCompatActivity {

    private List<Msg> msgList = new ArrayList<>();
    private RecyclerView msgRecyclerView;
    private EditText inputText;
    private Button send;
    private Button disconnect;
    private LinearLayoutManager layoutManager;
    private MsgAdapter adapter;

    public final static int NEW_MESSAGE = 1 ;
    public final static int OLD_MESSAGE_AI = 2 ;
    public final static int OLD_MESSAGE_I = 3 ;
    private String recvMessage;

    @SuppressLint("HandlerLeak")
    private Handler handler = new Handler(Looper.getMainLooper()){
        @Override
        public void handleMessage(Message msg){
            switch (msg.what){
                case NEW_MESSAGE:
                    msgList.add(new Msg((String)msg.obj,Msg.TYPE_RECEIVED));
                    adapter.notifyItemInserted(msgList.size()-1);
                    msgRecyclerView.scrollToPosition(msgList.size()-1);
                    break;
                case OLD_MESSAGE_AI:
                    msgList.add(new Msg((String)msg.obj,Msg.TYPE_RECEIVED));
                    adapter.notifyItemInserted(msgList.size()-1);
                    msgRecyclerView.scrollToPosition(msgList.size()-1);
                    break;
                case OLD_MESSAGE_I:
                    msgList.add(new Msg((String)msg.obj,Msg.TYPE_SEND));
                    adapter.notifyItemInserted(msgList.size()-1);
                    msgRecyclerView.scrollToPosition(msgList.size()-1);
                    break;
                default:
                    break;
            }

        }
    };

    /*设置一个线程定期监听登录时创建的TCPclient实例的变量recvMessage是否改变，若改变说明replika发来了新的消息
      此时需要更新UI*/
    private void SetListener(){
        new Thread(new Runnable() {
            @Override
            public void run() {
                while (true){
                    try {
                        if(LoginDataSource.tcpclient.getRecvMessage()!=null && !LoginDataSource.tcpclient.getRecvMessage().equals(recvMessage) ){
                            //说明有新的消息要处理，先把这个类的recvMessage更新，再给handler发送消息
                            recvMessage = LoginDataSource.tcpclient.getRecvMessage();
                            String[] blocks = recvMessage.split("%%");
                            for(String msg:blocks){
                                Message message = new Message();
                                message.what = NEW_MESSAGE;
                                message.obj = msg;
                                handler.sendMessage(message);
                            }
//                            Message message = new Message();
//                            message.what = NEW_MESSAGE;
//                            handler.sendMessage(message);
                        }
                        Thread.sleep(3000L);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
            }
        }).start();
    }


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_chat);

        msgRecyclerView = findViewById(R.id.msg_recycler_view);
        inputText = findViewById(R.id.input_text);
        send = findViewById(R.id.send);
        disconnect = findViewById(R.id.disconnect);
        layoutManager = new LinearLayoutManager(this);
        adapter = new MsgAdapter(msgList);

        msgRecyclerView.setLayoutManager(layoutManager);
        msgRecyclerView.setAdapter(adapter);

//        StyleManager s = StyleManager.getDefault();
//        LoadingDialog.initStyle(s);
//        LoadingDialog ld =new LoadingDialog(this);
//        ld.setLoadingText("载入中...").show();
//        try{
//            fetchHistory();
//            ld.loadSuccess();
//        }catch (Exception e){
//            ld.loadFailed();
//        }

        LoginDataSource.tcpclient.startRecvMessage();
        //设置监听replika发来的消息更新
        SetListener();

/*       我们还需要为button建立一个监听器，我们需要将编辑框的内容发送到 RecyclerView 上：
            ①获取内容，将需要发送的消息添加到 List 当中去。
            ②调用适配器的notifyItemInserted方法，通知有新的数据加入了，赶紧将这个数据加到 RecyclerView 上面去。
            ③调用RecyclerView的scrollToPosition方法，以保证一定可以看的到最后发出的一条消息。*/
        send.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String content = inputText.getText().toString();
                if(!content.equals("")) {
                    msgList.add(new Msg(content,Msg.TYPE_SEND));
                    adapter.notifyItemInserted(msgList.size()-1);
                    msgRecyclerView.scrollToPosition(msgList.size()-1);
                    inputText.setText("");//清空输入框中的内容
                    //给服务端发送这条消息

                    LoginDataSource.tcpclient.sendMessage(content);
                }
            }
        });

        disconnect.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });
    }

    @Override
    protected void onDestroy() {
        LoginDataSource.tcpclient.sendQuit();
        super.onDestroy();
    }

    private void fetchHistory(){
        //将历史信息分解
        String[] historyMessage = LoginDataSource.tcpclient.get_history();
        for(String string:historyMessage){
            if(string.substring(0,2).equals("2:")){
                string = string.substring(2);
                String[] blocks = string.split("%%");
                for(String msg:blocks){
                    Message message = new Message();
                    message.what = OLD_MESSAGE_AI;
                    message.obj = msg;
                    handler.sendMessage(message);
                }
            }else if(string.substring(0,2).equals("3:")){
                Message message = new Message();
                message.what = OLD_MESSAGE_I;
                message.obj = string.substring(2);
                handler.sendMessage(message);
            }
        }
    }

    private List<Msg> getData(){
        List<Msg> list = new ArrayList<>();
        list.add(new Msg("Hello",Msg.TYPE_RECEIVED));
        return list;
    }
}
