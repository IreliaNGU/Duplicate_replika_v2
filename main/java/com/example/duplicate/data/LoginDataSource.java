package com.example.duplicate.data;

import android.util.Log;

import com.example.duplicate.TCPclient.TCPClient;
import com.example.duplicate.data.model.LoggedInUser;

import java.io.IOException;

import static java.lang.Thread.sleep;

/**
 * Class that handles authentication w/ login credentials and retrieves user information.
 */
public class LoginDataSource {

    public static Exception err_info;

    public static TCPClient tcpclient;

    public Result<LoggedInUser> login(String username, String password) {

        try {
            // TODO: handle loggedInUser authentication
            tcpclient = new TCPClient(username,password);
            tcpclient.ConnectToServer();
            //隔5s检查是否执行结束，若没有结束则继续检查
            while (true){
                Log.d("LoginActivity","checking...");
                if (tcpclient.getResult().equals("Unknown")) {
                    sleep(5000);
                }else{
                    break;
                }
            }
            if(!tcpclient.getResult().equals("success")){
                Log.d("LoginActivity",tcpclient.getResult());
                throw new Exception(tcpclient.getResult());
            }
            LoggedInUser fakeUser =
                    new LoggedInUser(
                            java.util.UUID.randomUUID().toString(),
                            "replika user.");
            return new Result.Success<>(fakeUser);
        } catch (Exception e) {
            err_info = e ;
            Log.d("LoginActivity","catch Exception "+e);
            return new Result.Error(new IOException("Error logging in", e));
        }
    }

    public void logout() {
        // TODO: revoke authentication
    }
}