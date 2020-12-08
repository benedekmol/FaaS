import sqlalchemy
import time
import requests

def test_compute_function():
    time.sleep(0.1)


def invoke(request):
    #Create connection with the db
    pool = sqlalchemy.create_engine("mysql+pymysql://BenedekM:Bencuska@/cloudnativedb?unix_socket=/cloudsql/still-emissary-296814:europe-west3:cloudnativedb")
    connection = pool.connect()
    metadata = sqlalchemy.MetaData()
    datatable = sqlalchemy.Table('datatable', metadata, autoload=True, autoload_with=pool)
    query = sqlalchemy.select([datatable]).where(id == 999)


    #Data from request
    requestjson = request.get_json()
    insertId = requestjson['id']
    mysqlWriteData = requestjson['mysqlWrite']
    print(insertId)


    #Invoke another function
    functioninvoce_start = time.time()
    url = 'https://europe-west3-still-emissary-296814.cloudfunctions.net/function-1'
    headers = { "Content-Type" : "application/json","Accept":"text/plain" }
    payload = {"ts" : time.time()}
    r = requests.post(url, json=payload)
    functioninvocation_delay = (time.time() - functioninvoce_start) * 1000



    #Measure the time of executing a function
    compute_function_start = time.time()
    test_compute_function()
    compute_function_execution_delay = (time.time() - compute_function_start) * 1000
    
    pool.execute("use cloudnativedb")

    #Measure the time of writing to cloud sql
    dbwrite_start = time.time()
    #pool.execute("INSERT datatable (id,mysqlWrite) values(99, 99.999)")
    updatequery = sqlalchemy.update(datatable).values(mysqlWrite = mysqlWriteData).where(datatable.columns.id == 99)
    connection.execute(updatequery)
    dbwrite_delay = (time.time() - dbwrite_start) * 1000

    #Measure the time of reading from cloud sql
    dbread_start = time.time()
    queryResult = connection.execute(query)
    dbread_delay = (time.time() - dbread_start) * 1000



    results = {"function invocation blocking delay [ms]" : functioninvocation_delay,
                "compute function execution blocking [ms]" : compute_function_execution_delay,
                "db write delay [ms]" : dbwrite_delay,
                "db read delay [ms]" : dbread_delay,
                "request" : r.text}

    #insertquery = sqlalchemy.insert(datatable).values([
    #    {"id": insertId},
    #    {"functionBlocking" : functioninvocation_delay},
    #    {"computeFunctionExecution" : compute_function_execution_delay},
    #    {"mysqlWrite" : dbwrite_delay},
    #    {"mysqlRead" : dbread_delay}
    #])
    #insertQuery = sqlalchemy.insert(datatable).values((insertId, functioninvocation_delay, compute_function_execution_delay, dbwrite_delay, dbread_delay))
    insertQueryResult = connection.execute(f"insert into datatable values({insertId},{functioninvocation_delay},{compute_function_execution_delay},{dbwrite_delay},{dbread_delay})")

    print(results)
    return results

