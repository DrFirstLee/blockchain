import hashlib # hash 함수용 sha256 사용할 라이브러리
import json
from time import time
# from urlparse import urlparse
from urllib.parse import urlparse
import requests

class Blockchain(object):
    
    def __init__(self):
        self.chain = [] # chain에 여러 block들 들어옴
        self.current_transaction = [] # 임시 transaction 넣어줌
        self.nodes = set() # Node 목록을 보관
        # genesis block 생성
        self.new_block(previous_hash=1, proof=100)
        

    def register_node(self, address): # url 주소를 넣게 됨
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc) # set 자료형태 안에 목록을 저장
        
        
    def new_block(self, proof, previous_hash=None):
        # Creates a new Block and adds it to the chain
        block = {
            'index' : len(self.chain)+1,
            'timestamp' : time(), # timestamp from 1970
            'transactions' : self.current_transaction,
            'proof' : proof,
            'previous_hash' : previous_hash or self.hash(self.chain[-1]),
        }
        
        self.current_transaction = [] # 새로 블록이 생겼으니 이제 transaction 은 다시 초기화 
        self.chain.append(block)      # 기존 체인에 블록을 넣어 연결!! 블록체인  
        return block
    
    
    
    def new_transaction(self, sender, recipient, amount):
        # Adds a new transaction to the list of transaction
        self.current_transaction.append(
            {
                'sender' : sender, # 송신자
                'recipient' : recipient, # 수신자
                'amount' : amount, # 금액
                'timestamp':time()
            }
        )
        return self.last_block['index'] + 1    ## 거래가할떄마다 블록인댁스가 1늘어나??
    
    

    @staticmethod
    def hash(block):
        # Hashes a Block
        block_string = json.dumps(block, sort_keys=True).encode()
        # hash 라이브러리로 sha256 사용
        return hashlib.sha256(block_string).hexdigest()
    

    @property
    def last_block(self):
        # 체인의 마지막 블록 가져오기!!
        return self.chain[-1]
    
    def pow(self, last_proof):
        proof = 0
        # valid proof 함수 활용(아래 나옴), 맞을 때까지 반복적으로 검증
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
            
        return proof
    
    
    @staticmethod
    def valid_proof(last_proof, proof):
        # 전 proof와 구할 proof 문자열 연결
        guess = str(last_proof + proof).encode()
        # 이 hash 값 저장
        guess_hash = hashlib.sha256(guess).hexdigest()
        # 앞 4자리가 0000 이면 True 
        return guess_hash[:4] == "0000" # nonce
    
    
    def valid_chain(self, chain):
        last_block = chain[0] # 첫번째 제네시스 블록이 저장됨
        current_index = 1

        while current_index < len(chain): # 전체 체인 길이만큼 반복해 비교
            block = chain[current_index]
            print('%s' % last_block)
            print('%s' % block)
            print("\n--------\n")
            # check that the hash of the block is correct
            # hash 값을 비교해서 같지 않으면 거짓을 반환
            if block['previous_hash'] != self.hash(last_block):
                return False
            last_block = block
            current_index += 1
        return True
    
    ##  
    def resolve_conflicts(self):
        neighbours = self.nodes # 구동되는 노드들을 저장
        new_chain = None

        max_length = len(self.chain) # Our chain length
        for node in neighbours:
            tmp_url = "http://" + str(node) + '/chain' # url을 받아서 request 통해 체인 정보 저장
            response = requests.get(tmp_url)
            if response.status_code == 200: # 정상적으로 웹페이지와 교류가 되면 그 정보 저장
                length = response.json()['length']
                chain = response.json()['chain']
                ## 다른노드의 길이(length)가 내 노드의 길이(max_length) 보다 길고 and 내가 밸리드 체인이면
                if length > max_length and self.valid_chain(chain): # 긴 체인을 비교 >> 제일 긴놈만 살아남는다는것이 이뜻이다!!
                    max_length = length
                    ## 패배했다!! new_chain에 내가 받은 채인을 넣어주마!!
                    new_chain = chain
                
                else:
                    ## 내가 짱이다!!! 그런대 그럼 나머지 친구들도 다 바꿔줘야겠지?
                    ## 다른친구 바꾸는거는 각 노드단에서 보내는걸로!!
                    # self.nodes 가면 가바꿔줄수있는데!~~!??
                    ##################
                    1==1
#                 for nod in blockchain.nodes:
#                     print(nod)
#                     ## 다른노드에 보내디!
#                     headers = {'Content-Type' : 'application/json; charset=utf-8'}
#                     a = requests.get("http://" + nod + "/nodes/resolve", headers=headers)
#                     print(a.text)
            if new_chain:
                ###  ㅠㅠ 내가 패배했기에 새로운 채인을넣는다
                self.chain = new_chain
                return True

            return False