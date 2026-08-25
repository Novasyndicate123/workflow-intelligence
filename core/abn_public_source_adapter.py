from html.parser import HTMLParser
import re

class _ABNTableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows=[]; self._row=None; self._cell=False; self._text=[]
    def handle_starttag(self,tag,attrs):
        if tag=='tr': self._row=[]
        elif tag=='td' and self._row is not None: self._cell=True; self._text=[]
    def handle_data(self,data):
        if self._cell: self._text.append(data)
    def handle_endtag(self,tag):
        if tag=='td' and self._row is not None and self._cell:
            self._row.append(' '.join(''.join(self._text).split())); self._cell=False; self._text=[]
        elif tag=='tr' and self._row is not None:
            if self._row: self.rows.append(self._row)
            self._row=None

class ABNPublicSourceAdapter:
    def __init__(self, service_guid=None):
        self.service_guid=service_guid
        self.service_enabled=bool(service_guid)
        self.source_mode='web_service' if service_guid else 'public_search'
    def parse_results(self,html,query):
        if not isinstance(html,str) or not html.strip(): return []
        p=_ABNTableParser(); p.feed(html); results=[]
        for row in p.rows:
            if len(row)<2: continue
            abn=re.sub(r'\s+','',row[0])
            if not re.fullmatch(r'\d{11}',abn): continue
            name=row[1].strip()
            if not name: continue
            status = row[2] if len(row)>3 else ''
            location = row[3] if len(row)>3 else (row[2] if len(row)>2 else '')
            results.append(self.normalize({'business_name':name,'abn':abn,'status':status,'location':location,'query':query}))
        return results
    def normalize(self,data):
        return {'business_name':str(data.get('business_name','')).strip(),'abn':re.sub(r'\s+','',str(data.get('abn',''))),'status':str(data.get('status','')).strip().lower(),'location':str(data.get('location','')).strip(),'source':'ABN_LOOKUP_PUBLIC','query':str(data.get('query','')),'public_source_only':True,'source_mode':self.source_mode}
