#brute force on the Directories :: Abdallah Elsokary
try:
    import socket , requests , sys , time , threading , sqlite3 , os.path

except ModuleNotFoundError as e:
    print(e)

class DirCrawler:
    def __init__(self,Target,directories_list):
        self.Target = Target
        self.directories_list = directories_list

        
     #create database for Target 
    def create_database(self):
        conn = None
        try:
            if not os.path.exists("Databases/{0}_dirs.db".format(self.Target)):
                conn = sqlite3.connect("Databases/{0}_dirs.db".format(self.Target))
                c = conn.cursor()
                c.execute('''CREATE TABLE DIRS (dir TEXT NOT NULL);''')
                conn.commit()
        except sqlite3.Error as e:
            print(e)
            sys.exit(1)
        finally:
            if conn:
                conn.close()
                
    def insert_into_database(self,data):
        try:
            if os.path.exists("Databases/{0}_dirs.db".format(self.Target)):
                conn = sqlite3.connect("Databases/{0}_dirs.db".format(self.Target))
                c = conn.cursor()
                c.execute('''INSERT INTO DIRS VALUES ('%s');'''%(data))
                conn.commit()
        except sqlite3.Error as e:
            print(e)
            sys.exit(1)
        finally:
            if conn:
                conn.close()
        
     #opening Target    
    def Target_evaluate(self):
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            status_80 = s.connect_ex((self.Target,80))# check port 80 for http
            status_443 = s.connect_ex((self.Target,443))# Check port 443 for https
            s.close()
            if status_80 == 0:
                self.create_database() # createing data base for Target
                return 80
            elif status_443 == 0:
                return 443
            else:
                print('[FAIL]')
                print('[!] Error Cannot Reach The Target:{0}'.format(self.Target))
                sys.exit(1)
                
        except socket.error:
            print('[FAIL]')
            print('[!] Error Cannot Reach The Target:{0}'.format(self.Target))
            sys.exit(1)
            
       # reading directories list     
    def Reading_directories_list(self):
        try:
            with open(self.directories_list) as File:
                check = File.read().strip().split('\n')
                return check
        except IOError:
            print('[FAIL]')
            print('[!] Error: Failed to Read directories_list')
            sys.exit(1)
            
        # progressbar
    def progress(self,count, total,suffix=''):
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))
        percents = round(100.0 * count / float(total), 1)
        bar = '=' * filled_len + '-' * (bar_len - filled_len)
        time.sleep(0.5)
        sys.stdout.write('[%s] %s%s %s...\r' % (bar, percents, '%', suffix))
        sys.stdout.flush()
        
   
                
        #check directories
    def checkpath(self,d,cookies=None):
        try:
            valid_path = []
            target_ev = self.Target_evaluate()
            d_list = self.Reading_directories_list()
            #print("scanning for {0} dirs !!".format(len(d_list)))
            if target_ev == 80:
                response = requests.get('http://' + self.Target + '/' + d,cookies=cookies).status_code
                if response == 200:
                    if 'http://' + self.Target + '/' + d not in valid_path:
                        valid_path.append('http://' + self.Target + '/' + d)
                        #print('[+] http://' + self.Target + '/' + d )
                        self.insert_into_database('http://' + self.Target + '/' + d )
                    
                
            
            elif target_ev == 443:
                response = requests.get('https://' + self.Target + '/' + d,cookies=cookies).status_code
                print("Try:{0}".format(d),end='\r')
                if response == 200:
                     if 'https://' + self.Target + '/' + d not in valid_path:
                        valid_path.append('https://' + self.Target + '/' + d + ' [200]')
                        #print('[+] https://' + self.Target + '/' + d)
                        self.insert_into_database('https://' + self.Target + '/' + d )
                
        except Exception as e:
            print(e)
            print('[!] unexpected error occured ')
            sys.exit(1)
    
            
                
    def start_attack(self,*dirs):
        d_list = self.Reading_directories_list()
        count = 0
        for d in dirs:
            count+=1
            self.progress(count,len(self.Reading_directories_list()) / 5 )
            self.checkpath(d)
    
               
    def create_threads(self,t):
        dirs = self.Reading_directories_list()
        n = len(dirs)
        x = n // t
        m = n % t
        xs = [dirs[i:i+x] for i in range(0, n, x)]
        if m:
            xs[t-1:] = [dirs[-m-x:]]
        assert(sum([len(l) for l in xs]) == n)
        return [
        threading.Thread(target=self.start_attack, args=(l)) for l in xs ]  
    

c = DirCrawler('google.com','common.txt')
th = c.create_threads(5)
for t in th:
    t.start()
    
for t in th:
    t.join()
