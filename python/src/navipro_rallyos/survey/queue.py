"""Local SQLite offline queue for verified-user-captured proposals only.

Sync targets a NaviPRO staging server; never sends edits directly to OSM.
Server-side authentication/authorization, encrypted storage, file uploads and
retention controls must be implemented before real survey deployment.
"""
from __future__ import annotations
import sqlite3, json, hashlib
from pathlib import Path
from datetime import datetime
from typing import Any
from .core import QUESTS, assess_version_conflict, _string

class ObservationQueue:
    def __init__(self, db_path: str|Path):
        self.connection = sqlite3.connect(str(db_path))
        self.connection.execute('PRAGMA foreign_keys = ON')
        self.connection.execute('''CREATE TABLE IF NOT EXISTS survey_observations (
            observation_id TEXT PRIMARY KEY, task_id TEXT NOT NULL, route_revision_id TEXT NOT NULL,
            actor_id TEXT NOT NULL, quest_type TEXT NOT NULL, answer_json TEXT NOT NULL,
            observed_at TEXT NOT NULL, osm_element_type TEXT NOT NULL, osm_element_id INTEGER NOT NULL,
            observed_osm_version INTEGER NOT NULL, lat_e7 INTEGER NOT NULL, lon_e7 INTEGER NOT NULL,
            gps_accuracy_m REAL, evidence_sha256 TEXT,
            payload_sha256 TEXT NOT NULL, status TEXT NOT NULL, server_receipt TEXT
        )''')
        self.connection.commit()

    def close(self): self.connection.close()

    def enqueue(self, observation:dict[str,Any])->dict[str,Any]:
        required={'observation_id','task_id','route_revision_id','actor_id','quest_type','answer','observed_at','osm_element_type','osm_element_id','observed_osm_version','lat_e7','lon_e7','mode'}
        if not required.issubset(observation): raise ValueError('missing required observation fields')
        for field in ('observation_id','task_id','route_revision_id','actor_id'):
            _string(observation[field],field)
        if observation['mode'] not in ('PREP','REVIEW'):raise ValueError('field surveys are not allowed during LIVE')
        if observation.get('route_authority') is not False:raise ValueError('survey observation must declare route_authority=false')
        if observation['quest_type'] not in QUESTS: raise ValueError('unknown quest_type')
        if observation['osm_element_type'] not in ('node','way'):raise ValueError('invalid element type')
        for field in ('osm_element_id','observed_osm_version'):
            v=observation[field]
            if not isinstance(v,int) or isinstance(v,bool) or v<1:raise ValueError(f'invalid {field}')
        lat,lon=observation['lat_e7'],observation['lon_e7']
        if not isinstance(lat,int) or isinstance(lat,bool) or not -900000000<=lat<=900000000 or not isinstance(lon,int) or isinstance(lon,bool) or not -1800000000<=lon<=1800000000:
            raise ValueError('invalid E7 coordinates')
        ts=datetime.fromisoformat(_string(observation['observed_at'],'observed_at').replace('Z','+00:00'))
        if ts.tzinfo is None or ts.utcoffset() is None:raise ValueError('timestamp must include timezone')
        acc=observation.get('gps_accuracy_m')
        if acc is not None and (not isinstance(acc,(int,float)) or isinstance(acc,bool) or not 0<=acc<=100000):raise ValueError('invalid GPS accuracy')
        sha=observation.get('evidence_sha256')
        if sha is not None and (not isinstance(sha,str) or len(sha)!=64 or any(c not in '0123456789abcdef' for c in sha.lower())):raise ValueError('invalid evidence sha256')
        answer=observation['answer']
        if not isinstance(answer,(str,dict)) or not answer or isinstance(answer,str) and not answer.strip():raise ValueError('invalid answer')
        answer_json=json.dumps(answer,sort_keys=True,separators=(',',':'),ensure_ascii=False)
        canonical={k:observation.get(k) for k in sorted(required-{'answer'})}
        canonical.update(answer=answer, gps_accuracy_m=acc, evidence_sha256=sha,route_authority=False)
        payload_sha=hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
        row=self.connection.execute('SELECT payload_sha256,status FROM survey_observations WHERE observation_id=?',(observation['observation_id'],)).fetchone()
        if row:
            if row[0]!=payload_sha:raise ValueError('idempotency collision: same observation_id with different payload')
            return {'observation_id':observation['observation_id'],'status':row[1],'idempotent':True,'route_authority':False}
        self.connection.execute('''INSERT INTO survey_observations (observation_id,task_id,route_revision_id,actor_id,quest_type,answer_json,observed_at,osm_element_type,osm_element_id,observed_osm_version,lat_e7,lon_e7,gps_accuracy_m,evidence_sha256,payload_sha256,status)
          VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',(
          observation['observation_id'],observation['task_id'],observation['route_revision_id'],observation['actor_id'],observation['quest_type'],answer_json,observation['observed_at'],observation['osm_element_type'],observation['osm_element_id'],observation['observed_osm_version'],lat,lon,acc,sha,payload_sha,'PENDING_SYNC'))
        self.connection.commit()
        return {'observation_id':observation['observation_id'],'status':'PENDING_SYNC','idempotent':False,'route_authority':False}

    def list_pending(self)->list[dict[str,Any]]:
        c=self.connection.execute("SELECT observation_id,payload_sha256,task_id FROM survey_observations WHERE status='PENDING_SYNC' ORDER BY observed_at,observation_id")
        return [{'observation_id':a,'payload_sha256':b,'task_id':d} for a,b,d in c]

    def acknowledge_staging(self, observation_id:str,current_osm_version:int|None,receipt_id:str)->dict[str,Any]:
        """Call only after authenticated NaviPRO staging server has acknowledged a payload.

        Receipt alone never promotes VERIFIED; version mismatches quarantine it.
        """
        _string(receipt_id,'receipt_id')
        row=self.connection.execute('SELECT observed_osm_version,status FROM survey_observations WHERE observation_id=?',(observation_id,)).fetchone()
        if not row:raise KeyError('unknown observation')
        if row[1]!='PENDING_SYNC':raise ValueError('observation no longer pending')
        result=assess_version_conflict(row[0],current_osm_version)
        status='CONFLICT' if result['status']=='CONFLICT' else 'HOLD' if result['status']=='HOLD' else 'STAGED_REVIEW'
        self.connection.execute('UPDATE survey_observations SET status=?,server_receipt=? WHERE observation_id=?',(status,receipt_id,observation_id))
        self.connection.commit()
        return {'observation_id':observation_id,'status':status,'server_receipt':receipt_id,'route_authority':False}
