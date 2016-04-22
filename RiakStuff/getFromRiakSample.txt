import riak

myClient = riak.RiakClient(pb_port=8087, protocol='pbc', host='datatwo.csse.rose-hulman.edu')
myBucket = myClient.bucket('usernames')
userData = myBucket.get('lamberce')
print userData.data['name']