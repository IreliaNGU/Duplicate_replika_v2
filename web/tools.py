import selenium
import time


def Log_in_old(driver,user_email_or_phone,user_password):
    time.sleep(3)
    emailOrPhone = driver.find_element_by_xpath('//*[@id="emailOrPhone"]')
    emailOrPhone.click()
    emailOrPhone.clear()
    emailOrPhone.send_keys(user_email_or_phone)
    button_next_on_email = driver.find_element_by_xpath('//*[@id="loginForm"]/button')
    button_next_on_email.click()
    time.sleep(2)
    try:
        password = driver.find_element_by_xpath('//*[@id="login-password"]')
        password.click()
        password.clear()
        password.send_keys(user_password)
    except Exception as e:
        # 试图获取邮箱或电话不正确的错误
        email_err_info = driver.find_element_by_xpath('//*[@id="loginForm"]/div[2]/span[2]').text
        print('log in error from replika:'+ email_err_info)
        return email_err_info
    button_next_on_password = driver.find_element_by_xpath('//*[@id="loginForm"]/button')
    button_next_on_password.click()
    time.sleep(2)
    try:
        #尝试去找密码输入错误的提示
        password_error_info =driver.find_element_by_xpath('//*[@id="loginForm"]/div[3]/span[2]').text
        print('log in error from replika:' + password_error_info)
        return password_error_info
    except Exception as e:
        pass# 找不到，说明成功跳转

    try:
        #再次确认跳转成功
        time.sleep(5)
        # AI_name = driver.find_element_by_xpath('//*[@id="root"]/div/div[2]/aside[1]/div/div[1]/div/div[2]/button/h3').text
        return 'success'
    except Exception as e:
        print(e)
        driver.save_screenshot('errorlogin.png')
        return "fail with unknown reason.No error info on replika"



def Log_in_new(driver,sex):
    your_first_name= driver.find_element_by_xpath('//*[@id="name"]')
    your_first_name.click()
    your_first_name.clear()
    your_first_name.send_keys('Huang')
    your_email=driver.find_element_by_xpath('//*[@id="email"]')
    your_email.click()
    your_email.clear()
    your_email.send_keys('1@qq.com')
    your_new_password = driver.find_element_by_xpath('//*[@id="password"]')
    your_new_password.click()
    your_new_password.clear()
    your_new_password.send_keys('12345678')
    if(sex=='male'):
        your_pronouns = driver.find_element_by_xpath('//*[@id="pronoun-he"]')
        your_pronouns.click()
    elif(sex=='They'):
        your_pronouns = driver.find_element_by_xpath('//*[@id="pronoun-they"]')
        your_pronouns.click()
    button_get_start = driver.find_element_by_xpath('//*[@id="signupForm"]/button')
    button_get_start.click()