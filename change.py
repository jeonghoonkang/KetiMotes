#Autho: JungUk Choi

즉 set 이 모든 (node, seq) 의 경우의 수를 포함하면서,
거의 모든 패킷이 중복 패킷으로 (잘못) 처리되면서, 데이터가 들어가지 않는 현상 같습니다.


중복 처리를 좀 수정해서요, 각 node_id 별로 최근 N 개의 데이터만 캐싱해두는 식으로 변경을 해봤는데요,
smap 모듈이 없으니 빌드/테스트는 못해봤습니다. (파일 첨부합니다.)

변경된 부분은, 다음과 같습니다.

    CACHE_SIZE = 10  ## node_id 별로 최근 10개만 캐싱. (수치 변경 가능)

    def __init__(self, consumer):
        self.consumer = consumer
        TOSSerialClient.__init__(self)
        self.__cache = {}  ## 캐싱용 dict 객체 생성
    
    def is_cached(node_id, seq):  ## 중복인지 점검하는 메서드를 추가
        if node_id in self.__cache:
            return seq in self.__cache[node_id]

        return False

    def add_to_cache(node_id, seq):  ## 캐시에 저장하는 메서드를 추가
        if node_id not in self.__cache:
            self.__cache[node_id] = [seq]
        else:
            self.__cache[node_id].append(seq)
            while len(self.__cache[node_id]) > KetiMoteReceiver.CACHE_SIZE:  ## 캐싱 사이즈 (CACHE_SIZE)를 넘는다면 오래된 것부터 삭제
                self.__cache[node_id] = self.__cache[node_id][1:]

    def packetReceived(self, pkt):
        if len(pkt) != 29:
            return

        # pull apart the packet header, ignoring the tinyos part
        typ, serial_id, node_id, seq, bat, sensor = struct.unpack(">H6sHHH6s", pkt[9:29])
        if self.is_cached(node_id, seq): ## 캐싱된, 즉 중복된 데이터라면 그냥 return
            return
        else:
            self.add_to_cache(node_id, seq)  ## 아니라면 캐시에 추가
