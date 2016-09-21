#coding:utf-8
            
import rawes
import json
from datetime import datetime, timedelta
#from lookup import ip_lookup
            
NEEDED_EVENTS = [
        'video_start',  
        'system_off'
        ]
        
            
class EsAgent(object):
    def __init__(self, conf):
        self.es = rawes.Elastic(conf.get('elasticsearch', 'host'))
        self.new_docs = list()
        self.last_ip = ''
        
    def accept(self, p):
        # events which are ignored
        if p.get('event', '') not in NEEDED_EVENTS:
            return

        if p.get('event') in ['video_start', 'video_exit'] and p.get('location') == 'detail':
            return
        
        ###########################
        # get the index name
        ###########################
        try:
            if p.get('_device') == 'box_a11':
                t = p.get('_recv_time')
            else:
                t = datetime.fromtimestamp(int(p.get('_recv_time')))
            n = datetime.now()
        
            if t - n >= timedelta(1) or n - t >= timedelta(15):
                xlog.warn(0, 'time out of range{0}'.format(p))
                return
            index_name = t.strftime("%Y%m%d")
        except:
            xlog.warn(1, 'parse index_name error {0}'.format(p))
            return
        
        ###########################
        # get type name
        ###########################
        type_name = 'default' #p.get('_device', 'blank').lower().strip()
                
        ###########################
        # check unique_key
        ###########################
        uniq_id = p.get('_unique_key')
        if not uniq_id:
            xlog.warn(2, '_unique_key is not exists {0}'.format(p))
            return

        ###########################
        # items for the data
        ###########################
        data = {}

        # sn
        if 'sn' not in p:
            xlog.warn(3, 'sn missing {0}'.format(p))
            return
        data['sn'] = p.get('sn')

        # time, _recv_time
        try:
            data['time'] = p.get('time').strftime("%Y-%m-%dT%H:%M:%S.000Z")
            if p.get('_device') == 'box_a11':
                _recv_time = p.get('_recv_time')
            else:
                _recv_time = datetime.fromtimestamp(int(p.get('_recv_time')))

            data['_recv_time'] = _recv_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        except:
            xlog.warn(4, 'time or _recv_time convert error {0}'.format(p))
            return

        # event
        if 'event' not in p:
            xlog.warn(5, 'event missing {0}'.format(p))
            return
        data['event'] = p.get('event')

        # duration
        try:
            int(p['duration'])
            data['duration'] = p.get('duration')
        except:
            data['duration'] = ''

        # position
        try:
            int(p['position'])
            data['position'] = p.get('position')
        except:
            data['position'] = ''

        # others
        #if 'title' in p:
        #    data['title'] = p.get('title')
        for item in ['title', 'clip', 'ip', 'version', '_type', 'userid', '_device']:
            if item in p:
                data[item] = p.get(item)
        ###########################
        # send to es
        ###########################
        #try:
        #    self.es.post('/' + index_name + '/' + type_name + '/' + str(uniq_id), data = data)
        #except:
        #    xlog.warn(4, 'error when sending to elasticsearch {0}'.format(data))
        #    return

        #return

        self.new_docs.append({"update" : { "_index" : index_name, "_type" : type_name, "_id" : uniq_id}})
        self.new_docs.append({"doc": data, "doc_as_upsert": True})

        if len(self.new_docs) >= 20000:
            try:
                bulk_data = '\n'.join(map(json.dumps, self.new_docs))+'\n'
                self.es.post('/_bulk', data = bulk_data)
            except:
                xlog.warn(5, 'Failed when inserting to elasticsearch: {0}'.format(self.new_docs))
                return
            finally:
                self.new_docs = []

