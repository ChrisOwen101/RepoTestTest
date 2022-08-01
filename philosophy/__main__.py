from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from utils import open_link



#    Clicking on the first link in the main text of an English Wikipedia 
#    article, and then repeating the process for subsequent articles,
#    usually leads to the Philosophy article. 

#    In February 2016, this was true for 97% of all articles in Wikipedia

#         - https://en.wikipedia.org/wiki/Wikipedia:Getting_to_Philosophy


class API(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        q = ""
        if self.path != '/':
            q = self.path.split('?q=')[1]

        # Show a text input form
        self.wfile.write(bytes("<html><head><title>Getting to Philosophy</title></head>", "utf-8"))
        self.wfile.write(bytes("<body><form action='/'>", "utf-8"))
        self.wfile.write(bytes("<h2>Getting to Philosophy</h2>", "utf-8"))
        self.wfile.write(bytes('<p>"Clicking on the <strong>first link</strong> in the main text of an English Wikipedia article, and then repeating the process for subsequent articles, usually leads to the Philosophy article. In February 2016, this was true for 97% of all articles in Wikipedia" <a target="_blank" href="https://en.wikipedia.org/wiki/Wikipedia:Getting_to_Philosophy">more info</a></p>', "utf-8"))
        self.wfile.write(bytes("<input name='q' placeholder='Wikipedia entry' value='" + q + "' />", "utf-8"))
        self.wfile.write(bytes("<button type='submit'>Calculate</button></form>", "utf-8"))

        # If the user has submitted a query, show the results
        if self.path != '/' and self.path != '/?q=':
            route, degrees = getRoute(q)
            if (degrees == False) :
                self.wfile.write(bytes("<strong>" + q + " has no route to philosophy</strong><ol>", "utf-8"))
            else :
                self.wfile.write(bytes("<strong>" + str(degrees) + ": </strong><ol>", "utf-8"))
                for each in route:
                    self.wfile.write(bytes("<li><strong><a href='https://en.wikipedia.org/wiki/" + each[1] + "'>" + each[1] + "</a></strong> leads to</li>", "utf-8"))
                self.wfile.write(bytes("<li><strong>philosophy</strong></li></ol>", "utf-8"))
                self.wfile.write(bytes("<form action='/' method='post'><button type='submit'>Save output to S3 Bucket</button></form>", "utf-8"))

        self.wfile.write(bytes("</body></html>", "utf-8"))
    def do_POST(self):

        # If the user clicks 'Save output to S3 Bucket'.
        self.send_response(200)

# Follow the first links until you reach philosophy
def getRoute(q) :
    route = []
    wiki_link = 'https://en.wikipedia.org'
    wiki_philosophy = '/wiki/Philosophy'
    wiki_random = [q, 'https://en.wikipedia.org/wiki/' + q]
    counter = 1
    flag = False
    link = dict()
    link['a_text'] = wiki_random[0]
    link['a_href'] = wiki_random[1].replace(wiki_link,'')
    link['p_number'] = 0
    check_loop = set()
    while counter < 64:
        if link['a_href'] in check_loop:
            route.append('It is a loop.')
            flag = False
            break
        else :
            check_loop.add(link['a_href'])
        temp_link = wiki_link + link['a_href']
        route.append((str(counter) , link['a_text']))
        link, flag = open_link(temp_link)
        if flag == False :
            break
        if link['a_href'] == wiki_philosophy :
            counter += 1
            route.append((str(counter) , link['a_text']))
            flag = True
            break
        else:
            counter += 1
    if flag == True :
        return route, (str(len(route) + 1) + ' degrees between ' + q + ' and Philosophy')
    else :
        return route, False

# Start the server
if __name__ == "__main__":        
    hostName = "localhost"
    serverPort = os.environ.get("PORT") or 8080
    webServer = HTTPServer((hostName, str(serverPort)), API)
    print("Server started http://%s:%s" % (hostName, str(serverPort)))
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    webServer.server_close()
    print("Server stopped.")


