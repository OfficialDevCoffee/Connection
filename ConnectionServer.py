import socketserver
import threading

HOST = ''
PORT = 9009
lock = threading.Lock() #동기화 스레드

class UserManager:
    #사용자 관리 및 채팅 메세지 전송 담당 클래스
    #1. 채팅 입장 사용자의 등록
    #2. 채팅 퇴장 사용자의 삭제
    #3. 사용자 입, 퇴장의 관리
    #4. 사용자가 입력한 메세지를 전송

    def __init__(self):
        self.users = {} #사용자 등록 정보를 담을 사전 {id:(socket, address), ...}

    def addUser(self, username, connection, address): #사용자 ID를 self.users에 추가
        if username in self.users: #이미 등록되어 있다면
            connection.send('이미 등록된 사용자입니다.\n'.encode())
            return None

        #아니면 새로운 사용자 등록
        lock.acquire() #스레드 동기화 방지용 락
        self.users[username] = (connection, address)
        lock.release() #업뎃 후 락 해제

        self.sendMessageToAll('> [%s] 님이 입장하셨습니다.' %username)
        print('+++참여자 수 [%d]' %len(self.users))

        return username

    def removeUser(self, username): #사용자 ID를 self.users에서 제거
        if username not in self.users: #사용자가 등록되어 있지 않다면
            return

        #아니면 사용자 삭제
        lock.acquire()
        del self.users[username]
        lock.release()

        self.sendMessageToAll('> [%s] 님이 퇴장하셨습니다.' %username)
        print('+++참여자 수 [%d]' %len(self.users))

        pass

    def messageHandler(self, username, message): #전송 메세지를 처리하는 부분
        if message[0] != '/': #보낸 메세지의 첫 문자가 '/'가 아니면
            self.sendMessageToAll('[%s] %s' %(username, message))
            return

        if message.strip() == '/quit': #보낸 메세지가 커맨드인 'quit'이면
            self.removeUser(username)
            return -1

        pass

    def sendMessageToAll(self, message):
        for connection, address in self.users.values():
            connection.send(message.encode())
            pass
        pass

    pass

class TcpHandler(socketserver.BaseRequestHandler):
    usermanager = UserManager()

    def handle(self): #클라이언트가 접속시 클라이언트 주소 출력
        print('[%s] 연결됨' %self.client_address[0])

        try:
            username = self.registerUsername()
            message = self.request.recv(1024)
            while message:
                print(message.decode())
                if self.usermanager.messageHandler(username, message.decode()) == -1:
                    self.request.close()
                    break
                message = self.request.recv(1024)
                pass
            pass

        except Exception as e:
            print(e)
            pass

        print('[%s] 접속 종료' %self.client_address[0])
        self.usermanager.removeUser(username)
        pass

    def registerUsername(self):
        while True:
            self.request.send('> 서버: 사용하실 닉네임을 입력해주세요 < '.encode())
            username = self.request.recv(1024)
            username = username.decode().strip()

            if self.usermanager.addUser(username, self.request, self.client_address):
                return username
            pass
        pass

    pass

class Server(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def runServer():
    print('+++ Connection 채팅 서버를 시작합니다.')
    print('+++ 채팅 서버를 끝내려면 Ctrl-C를 누르세요.')

    try:
        server = Server((HOST, PORT), TcpHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print('--- Connection 채팅 서버를 종료합니다.')
        server.shutdown()
        server.server_close()
        pass
    pass

runServer()
