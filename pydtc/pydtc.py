import os
import asyncio
import jpype
from pydtc.connection import DBClient, APIClient
from pydtc.parallelize import ParallelDataFrame

def connect(db, host, user, password, options='', driver=None, lib_path=None, runtime_path=None):
    con = DBClient(db, host, user, password, options=options, driver=driver, lib_path=lib_path, runtime_path=runtime_path)
    con.connect()

    return con

def read_sql(con, sql):

    return con.read_sql(sql)

def clob_to_str(clob):
    try:
        sb = jpype.java.lang.StringBuilder()
        chars = jpype.JArray(jpype.JChar)(clob.length())
        cs = clob.getCharacterStream()
        cs.read(chars)
        sb.append(chars)
        cs.close()
        return sb.toString()
    except:
        return

def blob_to_file(blob, file_name, save_to):
    '''
    helper func to save the blob field into file.
    Param:
      blob: the blob field
      file_name: the file name
      save_to: the folder to save the file
    '''
    try:
        out = jpype.java.io.FileOutputStream(os.path.join(save_to, file_name))
        buff = blob.getBytes(1, blob.length())
        out.write(buff)
        out.close()
        return True
    except:
        return False

def create_temp(con, sql):

    con.create_temp(sql)

def load_temp(con, sql, df, chunksize=10000):

    con.load_temp(sql, df, chunksize=chunksize)

def load_batch(con, sql, df, chunksize=10000):

    con.load_batch(sql, df, chunksize=chunksize)


# speed up pandas cpu operation with multiprocessing especially for large set.
def p_apply(func, df, chunksize=10000, cores=None):
    try:
        pdf = ParallelDataFrame(df, num_ps=cores)

        return pdf.apply(func, chunksize=chunksize)
    except:
        raise
    finally:
        pdf.close()


def p_groupby_apply(func, df, groupkey, cores=None):
    try:
        pdf = ParallelDataFrame(df, num_ps=cores)

        return pdf.group_apply(func, groupkey)
    except:
        raise
    finally:
        pdf.close()


def api_get(urls, auth=None, loop=None):
    try:
        loop = loop or asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        api = APIClient(auth=auth, loop=loop)

        if isinstance(urls, list):
            _results = loop.run_until_complete(api.fetch_all(urls))

            results = [{url : r} for url, r in zip(urls, _results)]

        else:
            _results = loop.run_until_complete(api.fetch(urls))

            results = {urls : _results}

        return results
    except:
        raise
    finally:
        asyncio.run(api.close())


def api_update(url, data=None, method='put', auth=None, loop=None):
    try:
        loop = loop or asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        api = APIClient(auth=auth, loop=loop)

        results = loop.run_until_complete(api.update(url, data=data, method=method))

        return results
    except:
        raise
    finally:
        asyncio.run(api.close())