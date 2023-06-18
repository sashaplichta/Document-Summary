import pymongo
#samplesamplesampl
username = 'John Wick'
data = {
    #*** is missing a question/answer and relations
    #data structure is 
    #pdf_id : [timespent, associated_tags, quiz_id
    #quiz_id : {question_num : boolean}
    'pdf01' : ['1:00','science',['quiz_01','quiz_02']],
    'pdf02' : ['1:40','biology',['quiz_06','quiz_08']],
    'quiz_01' : {'question1': True,'question2': False, 'question3': True, 'score' : 90},
    'quiz_02' : {'question1': False,'question2': True, 'question3': False, 'score' : 95}
    }
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["DocuSum"]
col = mydb[username]
def insertData(data):
    #checks existing db if data already inserted
    duplicate = col.find_one(data)
    if duplicate:
        print("Duplicate found. Data not inserted")
    else:
        col.insert_one(data)
def dbcall(username: str) -> dict:
    #retrieves data using username
    key_to_search = username
    query = {key_to_search: {"$exists": True}}
    results = col.find(query)
    return results
