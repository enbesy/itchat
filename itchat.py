import itchat
from itchat.content import TEXT
from itchat.content import *
import sys
import time
import re
import importlib
import os
import time
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

importlib.reload(sys)
rec_tmp_dir = os.path.join(os.getcwd(), 'tmp/')
rec_msg_dict = {}
face_bug = None  # 针对表情包的内容
auto_reply = 0  #初始化开启或关闭自动回复

@itchat.msg_register([TEXT, PICTURE, FRIENDS, CARD, MAP, SHARING, RECORDING, ATTACHMENT, VIDEO], isFriendChat=True)
def handle_friend_msg(msg):
    global face_bug, init, auto_reply

    msg_time_rec = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 接受消息的时间
    msg_from = itchat.search_friends(userName=msg['FromUserName'])['NickName']  # 在好友列表中查询发送信息的好友昵称
    msg_create_time = msg['CreateTime']  # 信息发送的时间
    msg_id = msg['MsgId']  # 每条信息的id
    msg_type = msg['Type'] #信息的类型
    msg_content = None  # 储存信息的内容
    msg_share_url = None  # 储存分享的链接，比如分享的文章和音乐

    #打印信息的来源
    msg_send = msg_time_rec + "  " + msg_from
    print(msg_send)

    # 如果发送的消息是文本或者好友推荐
    if msg['Type'] == 'Text' or msg['Type'] == 'Friends':
        msg_content = msg['Text']
        print(msg_content)

    # 如果发送的消息是附件、视屏、图片、语音
    elif msg['Type'] == "Attachment" or msg['Type'] == "Video" \
            or msg['Type'] == 'Picture' \
            or msg['Type'] == 'Recording':
        msg_content = r"" + msg['FileName']
        msg['Text'](rec_tmp_dir + msg['FileName'])
        # msg_content = msg['FileName']  # 内容就是他们的文件名
        # msg['Text'](str(msg_content))  # 下载文件
        print(msg_content)

    elif msg['Type'] == 'Card':  # 如果消息是推荐的名片
        msg_content = msg['RecommendInfo']['NickName'] + '的名片'  # 内容就是推荐人的昵称和性别
        if msg['RecommendInfo']['Sex'] == 1:
            msg_content += '性别为男'
        else:
            msg_content += '性别为女'
        print(msg_content)

    elif msg['Type'] == 'Map':  # 如果消息为分享的位置信息
        x, y, location = re.search(
            "<location x=\"(.*?)\" y=\"(.*?)\".*label=\"(.*?)\".*", msg['OriContent']).group(1, 2, 3)
        if location is None:
            msg_content = r"纬度->" + x.__str__() + " 经度->" + y.__str__()  # 内容为详细的地址
        else:
            msg_content = r"" + location

    elif msg['Type'] == 'Sharing':  # 如果消息为分享的音乐或者文章，详细的内容为文章的标题或者是分享的名字
        msg_content = msg['Text']
        msg_share_url = msg['Url']  # 记录分享的url
        print(msg_share_url)
    face_bug = msg_content

    if msg_from == "enbesy":  # 如果是自己发的就没必要记录了
        if msg['Text'] == "道士出山":
            if auto_reply:
                auto_reply = 0
                itchat.send("关闭自动回复", toUserName='filehelper')
            else:
                itchat.send("已在山下了", toUserName='filehelper')
        elif msg['Text'] == "自闭修炼":
            if not auto_reply:
                auto_reply = 1
                itchat.send("开启自动回复", toUserName='filehelper')
            else:
                itchat.send("已习得自闭技能", toUserName='filehelper')
        elif msg['Text'] == "返璞归真":
            rec_msg_dict.clear()
            if not rec_msg_dict:
                itchat.send("清除成功", toUserName='filehelper')  # 发送给文件助手
    else:
        if auto_reply:    #开启自动回复
            # 向发送者发送消息并发给文件助手作备忘
            repetition = 0  #发送者不重复
            if rec_msg_dict:    #存储信息不为空
                for id in rec_msg_dict: #检查一段时间内发送者是否重复
                    if rec_msg_dict[id]['msg_from'] == msg_from:
                        repetition = 1
                        break

            if not repetition:  #如果不重复则自动回复
                itchat.send_msg('~~主人已开启工作模式...有事请直接留言~稍等一会..万一他"秒"回了哟~~急事的话赶紧电话炸醒他', toUserName=msg['FromUserName'])
                # return("reveived: %s" % msg['Text'])  # 返回的给对方的消息，msg["Text"]表示消息的内容

                # 统一记录信息发到文件助手作为备忘消息
                msg_book = "主人~主人~~~ 于" + msg_time_rec + "您有来自 " + msg_from + " 的消息" + "@记得查看喔~" + "\n"
                print(msg_book)
                itchat.send(msg_book, toUserName='filehelper')  # 发送给文件助手

        ##将信息存储在字典中，每一个msg_id对应一条信息
        rec_msg_dict.update(
            {
                msg_id: {
                    "msg_from": msg_from,
                    "msg_create_time": msg_create_time,
                    "msg_time_rec": msg_time_rec,
                    "msg_type": msg_type,
                    "msg_content": msg_content,
                    "msg_share_url": msg_share_url
                }
            }
        )

# 群聊信息监听
@itchat.msg_register([TEXT, PICTURE, FRIENDS, CARD, MAP, SHARING, RECORDING, ATTACHMENT, VIDEO], isGroupChat=True)
def handle_chatroom_msg(msg):
    global face_bug

    msg_time_rec = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 接受消息的时间
    msg_from = msg['ActualNickName']   #获取群聊里该用户昵称
    msg_create_time = msg['CreateTime']  # 信息发送的时间
    msg_id = msg['MsgId']  # 每条信息的id
    msg_type = msg['Type']  # 信息的类型
    msg_content = None  # 储存信息的内容
    msg_share_url = None  # 储存分享的链接，比如分享的文章和音乐


    # 如果发送的消息是文本或者好友推荐
    if msg['Type'] == 'Text' or msg['Type'] == 'Friends':
        msg_content = msg['Text']

    # 如果发送的消息是附件、视屏、图片、语音
    elif msg['Type'] == "Attachment" or msg['Type'] == "Video" \
            or msg['Type'] == 'Picture' \
            or msg['Type'] == 'Recording':
        msg_content = r"" + msg['FileName']
        msg['Text'](rec_tmp_dir + msg['FileName'])
        # msg_content = msg['FileName']  # 内容就是他们的文件名
        # msg['Text'](str(msg_content))  # 下载文件

    elif msg['Type'] == 'Card':  # 如果消息是推荐的名片
        msg_content = msg['RecommendInfo']['NickName'] + '的名片'  # 内容就是推荐人的昵称和性别
        if msg['RecommendInfo']['Sex'] == 1:
            msg_content += '性别为男'
        else:
            msg_content += '性别为女'

    elif msg['Type'] == 'Map':  # 如果消息为分享的位置信息
        x, y, location = re.search(
            "<location x=\"(.*?)\" y=\"(.*?)\".*label=\"(.*?)\".*", msg['OriContent']).group(1, 2, 3)
        if location is None:
            msg_content = r"纬度->" + x.__str__() + " 经度->" + y.__str__()  # 内容为详细的地址
        else:
            msg_content = r"" + location

    elif msg['Type'] == 'Sharing':  # 如果消息为分享的音乐或者文章，详细的内容为文章的标题或者是分享的名字
        msg_content = msg['Text']
        msg_share_url = msg['Url']  # 记录分享的url
    face_bug = msg_content


    ##将信息存储在字典中，每一个msg_id对应一条信息
    rec_msg_dict.update(
        {
            msg_id: {
                "msg_from": msg_from,
                "msg_create_time": msg_create_time,
                "msg_time_rec": msg_time_rec,
                "msg_type": msg_type,
                "msg_content": msg_content,
                "msg_share_url": msg_share_url
            }
        }
    )

#这个是用于监听是否有消息撤回
@itchat.msg_register(NOTE, isFriendChat=True, isGroupChat=True)
def send_msg_helper(msg):
    global face_bug
    # 这里如果这里的msg['Content']中包含消息撤回和id，就执行下面的语句
    if re.search(r"\<\!\[CDATA\[.*撤回了一条消息\]\]\>", msg['Content']) is not None:
        # 获取消息的id
        old_msg_id = re.search("\<msgid\>(.*?)\<\/msgid\>", msg['Content']).group(1)    # 在返回的content查找撤回的消息的id
        old_msg = rec_msg_dict.get(old_msg_id, {})   # 得到消息

        if len(old_msg_id) < 11:    # 如果发送的是表情包
            itchat.send_file(rev_tmp_dir + face_bug, toUserName='filehelper')
            #os.remove(rev_tmp_dir + face_bug)
        else:
            msg_body = "告诉你一个秘密~" + "\n" \
                       + old_msg.get('msg_from') + " 撤回了 " + old_msg.get("msg_type") + " 消息" + "\n" \
                       + old_msg.get('msg_time_rec') + "\n" \
                       + "撤回了什么 ⇣" + "\n" \
                       + r"" + old_msg.get('msg_content')
            # 如果是分享存在链接
            if old_msg['msg_type'] == "Sharing": msg_body += "\n就是这个链接➣ " + old_msg.get('msg_share_url')

            print(msg_body)
            # 将撤回消息发送到文件助手
            itchat.send(msg_body, toUserName='filehelper')
            # 有文件的话也要将文件发送回去
            # 判断文msg_content是否存在，不存在说明可能是
            if os.path.exists(os.path.join(rec_tmp_dir, old_msg['msg_content'])):
                if old_msg["msg_type"] == "Picture":
                    itchat.send_image(os.path.join(rec_tmp_dir, old_msg['msg_content']), toUserName="filehelper")
                elif old_msg["msg_type"] == "Video":
                    itchat.send_video(os.path.join(rec_tmp_dir, old_msg['msg_content']), toUserName="filehelper")
                elif old_msg["msg_type"] == "Attachment" \
                        or old_msg["msg_type"] == "Recording":
                    itchat.send_file(os.path.join(rec_tmp_dir, old_msg['msg_content']), toUserName="filehelper")

                #os.remove(rev_tmp_dir + old_msg['msg_content'])
            # 删除字典旧消息
            #rec_msg_dict.pop(old_msg_id)


# 每隔五种分钟执行一次清理任务
def clear_cache():
    # 当前时间
    cur_time = time.time()
    # 遍历字典，如果有创建时间超过x分钟或x秒的记录，删除，非文本的话，连文件也删除
    for key in list(rec_msg_dict.keys()):
        if int(cur_time) - int(rec_msg_dict.get(key).get('msg_create_time')) > 1800:
            if not rec_msg_dict.get(key).get('msg_type') == 'Text':
                file_path = os.path.join(rec_tmp_dir, rec_msg_dict.get(key).get('msg_content'))
                print(file_path)
                if os.path.exists(file_path):
                    os.remove(file_path)
            rec_msg_dict.pop(key)

# 开始轮询任务
def start_schedule():
    sched.add_job(clear_cache, 'interval', minutes=31) #例如minutes=2
    sched.start()

# 退出停止所有任务并清空缓存文件夹
def after_logout():
    print("注销成功: 正在清空缓存文件夹...")
    sched.shutdown()
    shutil.rmtree(rec_tmp_dir)
    print("完成任务，进程关闭")

if __name__ == '__main__':
    sched = BlockingScheduler()
    if not os.path.exists(rec_tmp_dir):
        os.mkdir(rec_tmp_dir)
    itchat.auto_login(hotReload=True, exitCallback=after_logout)
    itchat.run(blockThread=False)
    start_schedule()


