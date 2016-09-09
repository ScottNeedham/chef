
class zone_cache():

    def  __init__(self, num_buckets=512):
        """
        Initializes a Map with the given number of buckets.
        """
        self.aMap = []
        for i in range(0, num_buckets):
            self.aMap.append([])
        

    def add_entry(self, lat, lon, zone, fleet, leadtime):
        entry = (zone, leadtime)
        key = (lat, lon, fleet)
        self.set (key,  entry)

    def hash_key(self, key):
        """Given a key this will create a number and then convert it to
        an index for the aMap's buckets."""
        return hash(key) % len(self.aMap)

    def get_bucket(self, key):
        """Given a key, find the bucket where it would go."""
        bucket_id = self.hash_key(key)
        return self.aMap[bucket_id]

    def get_slot(self, key, default=None):
        """
        Returns the index, key, and value of a slot found in a bucket.
        Returns -1, key, and default (None if not set) when not found.
        """
        bucket = self.get_bucket(key)

        for i, kv in enumerate(bucket):
            k, v = kv
            if key == k:                
                return i, k, v

        return -1, key, default

    def get(self, key, default=None):
        """Gets the value in a bucket for the given key, or the default."""
        i, k, v = self.get_slot(key, default=default)
        return v

    def set(self, key, value):
        """Sets the key to the value, replacing any existing value."""
        bucket = self.get_bucket(key)
        i, k, v = self.get_slot(key)

        if i >= 0:
            # the key exists, replace it
            bucket[i] = (key, value)
        else:
            # the key does not, append to create it
            bucket.append((key, value))

    def delete(self, key):
        """Deletes the given key from the Map."""
        bucket = self.get_bucket(key)

        for i in range(len(bucket)):
            k, v = bucket[i]
            if key == k:
                del bucket[i]
                break

    def list(self):
        """Prints out what's in the Map."""
        for bucket in self.aMap:
            if bucket:
                for k, v in bucket:
                    print k, v



if __name__ == "__main__":
    
    try:
        lat =  "45.34100000"
        lon =  "-75.34100000"
        zone = 1
        fleet = 2
        leadtime = 10

        mycache =  zone_cache()
        for i in range(100):

            mycache.add_entry(lat, lon, zone, fleet, leadtime)

            lat = str( float(lat) + 1.0000)
            lon =  str( float(lon) + 1.0000)
            zone += 1
            fleet += 1
            leadtime += 2

        lat = str ( 90.34100)
        lon = str ( -30.34100)
     
        mycache.list()

        v = mycache.get( (lat, lon, 47 ))

        if v != None:
            print ' v = %d %d  ' % (v)

    except Exception as e:
      print 'Exception ', str(e)





