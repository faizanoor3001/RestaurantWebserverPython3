from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base , Restaurant , Menu

memory = []

restaurantListPage = '''
            <!DOCTYPE html>
            <title>Restaurants!!</title>
            <body>
            <h3>{}</h3>
            <a href='/restaurants/new'><h3><ul>Make a new restaurant here</ul></h3></a>
            </body>
            </html>
            '''

newRestaurantPage = '''
            <!DOCTYPE html>
            <title>Make a new Restaurant</title>
            <body>
            <h1>Make a New Restaurant</h1>
            <form method = POST action = '/restaurants/new'>
            <input name = 'restaurantName' type = 'text'>
            <input name = 'Create' type = 'submit'>
            </form>
            </body>
            </html>
            '''

renameRestaurantPage = '''
            <!DOCTYPE html>
            <title>Rename a Restaurant</title>
            <body>
            <h1>Rename {} </h1>
            <form method = POST action = '/restaurants/{}/edit'>
            <input name = 'toRestaurantName' type = 'text'>
            <input name = 'Rename' type = 'submit'>
            </form>
            </body>
            </html>
            '''
deleteRestaurantPage = '''
            <!DOCTYPE html>
            <title> Delete a Restaurant </title>
            <body>
            <h1><em>Are you sure you want to delete {} ?</em><h1>
            <form method = POST action = '/restaurants/{}/delete'>
            <input name = 'Delete' type = 'submit'>
            </form>
            </body>
            </html>
            '''


engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()


class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path.endswith('/restaurants'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
           
            restaurantList = session.query(Restaurant).all()
            for restaurant in restaurantList:
                memory.append(restaurant.name)
                memory.append("<a href='/restaurants/%s/edit'><ul>Edit</ul></a>" % restaurant.id)
                memory.append("<a href='/restaurants/%s/delete'><ul>Delete</ul></a>" % restaurant.id)
            

            output = restaurantListPage.format("<br/>".join(memory))
            memory.clear()
            self.wfile.write(output.encode())
            return

        if self.path.endswith('/restaurants/new'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            output = newRestaurantPage
            self.wfile.write(output.encode())

        if self.path.endswith('/edit'):
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            restaurantId = self.path.split("/")[2]
            restaurantNameToBeRenamed = session.query(Restaurant).filter_by( id = restaurantId).one()

            output = renameRestaurantPage.format(restaurantNameToBeRenamed.name,restaurantId)
            self.wfile.write(output.encode())

        if self.path.endswith('/delete'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            restaurantId = self.path.split("/")[2]
            restaurantNameToBeDeleted = session.query(Restaurant).filter_by( id = restaurantId).one()

            output = deleteRestaurantPage.format(restaurantNameToBeDeleted.name,restaurantId)
            self.wfile.write(output.encode())


        else:
            self.send_error(404, 'File Not Found: %s' % self.path)


    def do_POST(self):
        #how long is the data
        if self.path.endswith('/restaurants/new'):
            length = int(self.headers.get('Content-length',0))

            #Extract the data part, read and parse 
            data = self.rfile.read(length).decode()
            message = parse_qs(data)["restaurantName"][0]
            print(message)
            message = message.replace("<", "&lt;")
            newRestaurant = Restaurant(name = message)
            session.add(newRestaurant)
            session.commit()
            self.send_response(301)
            self.send_header('Location', '/restaurants')
            self.end_headers()
   

        if self.path.endswith('/edit'):
            length = int(self.headers.get('Content-length',0))

            #Extract the data part, read and parse 
            data = self.rfile.read(length).decode()
            newRestaurantName = parse_qs(data)["toRestaurantName"][0]
            print(newRestaurantName)
            restaurantId = self.path.split("/")[2]
            existingRestaurant = session.query(Restaurant).filter_by(id = restaurantId).one()
            existingRestaurant.name = newRestaurantName
            session.add(existingRestaurant)
            session.commit()
            self.send_response(301)
            self.send_header('Location', '/restaurants')
            self.end_headers()

        
        if self.path.endswith('/delete'):
            # length = int(self.headers.get('Content-length',0))
            # data = self.rfile.read(length).decode()
            restaurantId = self.path.split("/")[2]
            restaurantToBeDeleted = session.query(Restaurant).filter_by(id = restaurantId).one()
            print(restaurantToBeDeleted.name)
            session.delete(restaurantToBeDeleted)
            session.commit()
            self.send_response(301)
            self.send_header('Location', '/restaurants')
            self.end_headers()

        return
    #except:
        #pass


def main():
    try:
        port = 7008
        httpd = HTTPServer(('', port), WebServerHandler)
        print ("Web Server running on port %s" % port)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print (" ^C entered, stopping web server....")
        httpd.socket.close()

if __name__ == '__main__':
    main()
