from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Hotel, Base, HotelInfo, User

engine = create_engine('sqlite:///hotelcatalogwithusers.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create a fake user

User1 = User(name="John Newman", email="newjohnnyboy@sublime.com", picture='https://www.google.gr/url?sa=i&rct=j&q=&esrc=s&source=images&cd=&cad=rja&uact=8&ved=2ahUKEwih4Jqh0ezdAhURPVAKHST5A4AQjRx6BAgBEAU&url=https%3A%2F%2Funsplash.com%2Fsearch%2Fphotos%2Fphoto&psig=AOvVaw1XUxbWhN7npvHcyw-0wmUa&ust=1538737273751160')   # noqa
session.add(User1)
session.commit()

# Create a fake hotel
hotel1 = Hotel(name="Seaview", user_id=1)
session.add(hotel1)
session.commit()

# Create Information for this hotel

hotelinfo1 = HotelInfo(user_id=1, name="Standard Single Room", description="Available for one person with partial view of the sea,breakfast included", price="45", category="Single Room", hotel=hotel1)  # noqa

session.add(hotelinfo1)
session.commit()

hotelinfo2 = HotelInfo(user_id=1, name="Superior Single Room", description="Available for one person with unobstructed view of the sea,breakfast included", price="55", category="Single Room", hotel=hotel1)  # noqa

session.add(hotelinfo2)
session.commit()

hotelinfo3 = HotelInfo(user_id=1, name="Standard Double Room", description="Available for two people with partial view of the sea,breakfast included.You can choose between a double bed and two single beds.You can add a small bed for your baby until 2 years old free of charge.", price="60", category="Double Room", hotel=hotel1)  # noqa

session.add(hotelinfo3)
session.commit()

hotelinfo4 = HotelInfo(user_id=1, name="Superior Double Room", description="Available for two people with unobstructed view of the sea,breakfast included.You can choose between a double bed and two single beds.You can add a small bed for your baby until 2 years old free of charge.", price="70", category="Double Room", hotel=hotel1)  # noqa

session.add(hotelinfo4)
session.commit()

hotelinfo5 = HotelInfo(user_id=1, name="Standard Triple Room", description="Available for three people with partial view of the sea,breakfast included.You can choose between three single beds or one double and a single.You can add a small bed for your baby until 2 years old free of charge.", price="90", category="Triple Room", hotel=hotel1)  # noqa

session.add(hotelinfo5)
session.commit()


hotelinfo6 = HotelInfo(user_id=1, name="Superior Triple Room", description="Available for three people with unobstructed view of the sea,breakfast included.You can choose between three single beds or one double and a single.You can add a small bed for your baby until 2 years old free of charge.", price="100", category="Triple Room", hotel=hotel1)  # noqa

session.add(hotelinfo6)
session.commit()

hotelinfo7 = HotelInfo(user_id=1, name="Standard Four Bed Room", description="The ideal choice for families.Available for four people with partial view of the sea,breakfast included.There are two bedrooms one with a double bed and another with two single beds.You can add up to two small beds for your babies until 2 years old free of charge.", price="120", category="Four Bed Room", hotel=hotel1)  # noqa

session.add(hotelinfo7)
session.commit()

hotelinfo8 = HotelInfo(user_id=1, name="Junior Suite", description="Available for six people with unobstructed view of the sea,breakfast included.There are three bedrooms with king size beds and a sitting room.You can add up to three small beds for your babies until 2 years old free of charge.", price="250", category="Suite", hotel=hotel1)  # noqa

session.add(hotelinfo8)
session.commit()

hotelinfo9 = HotelInfo(user_id=1, name="Superior Suite", description="Available for six people with unobstructed view of the sea,breakfast included.There are three bedrooms with king size beds and a sitting room with a fireplace and a big dining table.You can add up to three small beds for your babies until 2 years old free of charge.", price="350", category="Suite", hotel=hotel1)  # noqa

session.add(hotelinfo9)
session.commit()


print "added hotel information!"
