import datetime
import os, sys

if __name__ == "__main__":  
    app_dir = os.path.dirname(__file__) + "/.."
    sys.path.append (app_dir )


from base.base_model import BaseModel



class FareTemplate(BaseModel):
    fare_template_id = 0
    pick_up_time = None
    pick_up_date = None
    account_number = u''
    customer_number = 0
    account_name = u''
    booker_name = u''
    passenger_name = u''
    passenger_email = u''
    passenger_phone = u''
    enable_sms = 0
    disable_call_out = 0
    vip_number = u''
    as_directed = 0
    fleet_number = 0
    vehicle_number = 0
    driver_number = 0
    priority = 0
    vehicle_types = None
    driver_types = None
    addresses = None
    notes = u''
    vehicles_count = 0
    passengers_count = 0
    will_call = 0
    quick_return = 0
    contract_number = u''
    payment_method_id = u''
    active = 0
    flat_rate = 0

    def __init__(self, fare_template_id=0):
        super(FareTemplate, self).__init__()
        self.fare_template_id = fare_template_id
        self.pick_up_time = datetime.datetime.now().time()
        self.pick_up_date = datetime.datetime.now().date()
        self.pick_up_datetime = datetime.datetime.now()
        self.vehicle_types = []
        self.driver_types = []
        self.addresses = []
        self.payment_method_id = 'CA'
        self.active = 1
        self.priority = 1

    def __dir__(self):
        return ['fare_template_id', 'pick_up_datetime', 'pick_up_time', 'pick_up_date', 'account_number', 'customer_number', 'account_name',
                'booker_name', 'passenger_name', 'passenger_email', 'passenger_phone', 'enable_sms', 'disable_call_out',
                'vip_number', 'as_directed', 'fleet_number', 'vehicle_number', 'driver_number', 'priority',
                'vehicle_types', 'driver_types', 'addresses', 'notes', 'vehicles_count', 'passengers_count',
                'will_call', 'quick_return', 'contract_number', 'payment_method_id', 'active', 'flat_rate']

  

    def to_api_dict(self):
        return {
            'fare_template_id': self.fare_template_id,
            'pick_up_datetime': self.format_value(self.pick_up_datetime),
            'pick_up_time': self.format_value(self.pick_up_time),
            'pick_up_date': self.format_value(self.pick_up_date),
            'account_number': self.account_number,
            'customer_number': self.customer_number,
            'account_name': self.account_name,
            'booker_name': self.booker_name,
            'passenger_name': self.passenger_name,
            'passenger_email': self.passenger_email,
            'passenger_phone': self.passenger_phone,
            'enable_sms': self.enable_sms,
            'disable_call_out': self.disable_call_out,
            'vip_number': self.vip_number,
            'as_directed': self.as_directed,
            'fleet_number': self.fleet_number or 0,
            'vehicle_number': self.vehicle_number or 0,
            'driver_number': self.driver_number or 0,
            'priority': self.priority,
            'vehicle_types': self.vehicle_types,
            'driver_types': self.driver_types,
          
            'notes': self.notes,
            'vehicles_count': self.vehicles_count,
            'passengers_count': self.passengers_count,
            'will_call': self.will_call,
            'quick_return': self.quick_return,
            'contract_number': self.contract_number,
            'payment_method_id': self.payment_method_id,
            'active': self.active,
            'flat_rate': self.flat_rate
        }

    def to_dict(self):
        result = self.to_api_dict()
       
        return result

    @property
    def pick_up_point(self):
        return self.addresses and self.addresses[0] or None

    @property
    def drop_off_point(self):
        return self.addresses and len(self.addresses) >= 2 and self.addresses[-1] or None

    @property
    def viases(self):
        return self.addresses and (self.addresses[1:-1] if not self.as_directed else self.addresses[1:]) or []

    @property
    def template_viases(self):
        viases = self.viases
     
        return viases

    def pre_render(self):
        if self.pick_up_point:
            self._add_route_item_fields('pick_up', self.pick_up_point)
        if self.drop_off_point:
            self._add_route_item_fields('destination', self.drop_off_point)
        if self.viases:
            self._add_vias_route_item_fields()
        self._add_additional_information()
        if self.vehicle_types:
            self.vehicle_types = [int(i) for i in self.vehicle_types]
        if self.driver_types:
            self.driver_types = [int(i) for i in self.driver_types]
        self.pick_up_passengers = self.passengers_count
        self.time = self.pick_up_time
        return self

    def init_properties(self):
        dt = datetime.datetime.now()
        self.date = dt.date()
        self.time = dt.time()

    def _add_route_item_fields(self, prefix, route_item):
        setattr(self, prefix, route_item.address)
        setattr(self, prefix + '_building_name', route_item.building_name)
        setattr(self, prefix + '_lat', route_item.latitude)
        setattr(self, prefix + '_lng', route_item.longitude)
        setattr(self, prefix + '_apartment_number', route_item.apartment_code)
        setattr(self, prefix + '_street_number', route_item.street_number)
        setattr(self, prefix + '_street_name', route_item.street_name)
        setattr(self, prefix + '_city', route_item.city)
        setattr(self, prefix + '_country', route_item.country)
        setattr(self, prefix + '_zip_code', route_item.zip_code)
        setattr(self, prefix + '_apartment_code', route_item.apartment_code)
        setattr(self, prefix + '_state', route_item.state)
        setattr(self, prefix + '_zone', route_item.zone)
        if prefix == 'pick_up':
            setattr(self, prefix.replace('_', '') + '_building_type', route_item.building_type)
            setattr(self, prefix.replace('_', '') + '_building_number', route_item.building_number)
        elif prefix == 'destination':
            setattr(self, prefix + '_building_type', route_item.building_type)
            setattr(self, prefix + '_building_number', route_item.building_number)

    def _add_vias_route_item_fields(self):
        i = 0
        for vias in self.viases:
            i += 1
            vias.lat = vias.latitude
            vias.lng = vias.longitude
            setattr(self, 'vias{0}'.format(i), vias.to_dict())

    def _add_additional_information(self):
        if self.driver_number:
            self.call_number = self.driver_number
        elif self.vehicle_number:
            self.cab_no = self.vehicle_number
        self.exceptions = self.driver_types
        self.fleet = self.fleet_number
        self.phone_account = self.account_number
        self.email = self.passenger_email
        self.mobile = self.passenger_phone
        self.booker = self.booker_name
        self.vip_number_string = self.vip_number


if __name__ == "__main__":
    try:

        fare = FareTemplate()

        mydic = fare.to_dict()
        print ( ' fare {0} dic{1}'.format ( fare, mydic ) )

    except Exception as e:
        sys.stdout.write(" *** main {0} \n".format( str(e) ))