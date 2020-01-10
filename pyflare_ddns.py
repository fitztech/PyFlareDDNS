import http.client, json

CF_API_URL = "api.cloudflare.com"
CF_API_TOKEN = "<Cloudflare OAuth Token>" 
IPIFY_API_URL = "api.ipify.org"

zones = {
    "example.com": { 
        "records" : {
            "foo.example.com": {"type": "A", "ttl": "1", "proxied": "true"},
            "bar.example.com": {"type": "A", "ttl": "1", "proxied": "true"} 
        }
    }
}

cfHeaders = {
    "Content-Type":"application/json",
    "Authorization":"Bearer " + CF_API_TOKEN
}

#Get IP from ipify API
ipifySession = http.client.HTTPSConnection(IPIFY_API_URL)
ipifySession.request("GET", "/")
currentIP = ((ipifySession.getresponse()).read()).decode('utf-8')
if ipifySession:
    ipifySession.close()

cfSession = http.client.HTTPSConnection(CF_API_URL)
for zone in zones:
    #Get zone ID, to be used in later requests
    cfSession.request("GET", "/client/v4/zones?name=" + zone, body = None, headers = cfHeaders)
    zoneID = json.loads(cfSession.getresponse().read())['result'][0]['id']
        
    for record in zones[zone]['records'].items():
        #Get record ID, required to update records
        cfSession.request("GET", "/client/v4/zones/" + zoneID + "/dns_records?type=" + record[1]['type'] + "&name=" + record[0], body = None , headers = cfHeaders)
        result = json.loads(cfSession.getresponse().read())['result'][0]

        if result['content'] != currentIP:
            #Update record and print pretty result
            cfBody = '{"type":"' + record[1]['type'] + '","name":"' + record[0] + '","content":"' + currentIP + '","ttl":' + record[1]['ttl'] + ',"proxied":' + record[1]['proxied'] + '}'
            cfSession.request("PUT", "/client/v4/zones/" + zoneID + "/dns_records/" + result['id'], body = cfBody, headers = cfHeaders)
            result = cfSession.getresponse().read()
        
cfSession.close() 