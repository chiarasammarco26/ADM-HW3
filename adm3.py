from tqdm import tqdm
import requests
import bs4
from bs4 import BeautifulSoup
import os
from datetime import datetime
import time

root_url = "https://www.atlasobscura.com"

def saveHtmlToFolder(folder_number, place_name, url):
    """
    description:
        function that is used for saving html content to local directory

    params:
        - folder_name: number of page to save file in same directory;
        - place_name: name of place to name saved file;
        - url: url that was retrieved from 'Places.txt' file.
    output:
        logging info about saving files
    """
    try:
        # '/places/city-hall-station' => '/city-hall-station'
        place_name = place_name[8:]
        # return path of the current folder
        current_path = os.getcwd()

        # if page folder is not exist => create new folder
        directory = os.path.join(current_path, "places", str(folder_number))
        if not os.path.exists(directory):
            os.makedirs(directory)

        # full path for saving the file
        file_name = os.path.join(current_path, "places", str(folder_number), place_name)
        #print(file_name)
        # take html content
        content = requests.get(url).content
        with open(file_name+".html", 'wb') as f:
            f.write(content)
        # info about saving
        print(f"'{url}'" + " is saved to " + f"'{file_name}'")
        return 0
    except Exception as e: 
        print(e)
        return folder_number
    
def list_to_string(ls):
    """
    description:
        casting list to string
    params:
        - ls: list with data
    return:
        converted string of list
    """
    line = "["
    for l in ls:
        line += f"'{l}'"
        line += ", "
    line = line[:-3] + "]"
    if ls == []:
        return "none"
    return line
    
class Place(object):
    def __init__(self, 
                 placeName, 
                 placeTags, 
                 numPeopleVisited, 
                 numPeopleWant, 
                 placeDesc, 
                 placeShortDesc, 
                 placeNearby, 
                 placeAddress, 
                 placeAlt, 
                 placeLong, 
                 placeEditors, 
                 placePubDate,
                 placeRelatedLists,
                 placeRelatedPlaces,
                 placeURL):
        self.placeName = placeName
        self.placeTags = placeTags
        self.numPeopleVisited = numPeopleVisited
        self.numPeopleWant = numPeopleWant
        self.placeDesc = placeDesc
        self.placeShortDesc = placeShortDesc
        self.placeNearby = placeNearby
        self.placeAddress = placeAddress
        self.placeAlt = placeAlt
        self.placeLong = placeLong
        self.placeEditors = placeEditors
        self.placePubDate = placePubDate
        self.placeRelatedLists = placeRelatedLists
        self.placeRelatedPlaces = placeRelatedPlaces
        self.placeURL = placeURL
        
    def to_string(self):
        line = " \t ".join([self.placeName, 
                 list_to_string(self.placeTags), 
                 str(self.numPeopleVisited), 
                 str(self.numPeopleWant), 
                 self.placeDesc, 
                 self.placeShortDesc, 
                 list_to_string(self.placeNearby), 
                 self.placeAddress, 
                 str(self.placeAlt), 
                 str(self.placeLong), 
                 list_to_string(self.placeEditors), 
                 str(self.placePubDate),
                 list_to_string(self.placeRelatedLists),
                 list_to_string(self.placeRelatedPlaces),
                 self.placeURL])
        return line
    
def func_placeName(soup):
    placeName = ""
    try: 
        placeName = soup.find("h1", {"class": "DDPage__header-title"}).text
    except:
        print("placeName")
        placeName = ""
    finally:
        return placeName

def func_placeTags(soup):
    placeTags = []
    try: 
        placeTags = [tag.text.strip() for tag in soup.find_all("a", {"class": "itemTags__link js-item-tags-link"})]
    except:
        print("placeTags")
        placeTags = []
    finally:
        return placeTags

def func_numPeople(soup):
    numPeopleVisited = ""
    numPeopleWant = ""
    try: 
        visitance = [tag.text for tag in soup.find_all("div", {"class": "title-md item-action-count"})]
        numPeopleVisited = visitance[0]
        numPeopleWant = visitance[1]
    except:
        print("numPeopleVisited, numPeopleWant")
        numPeopleVisited = ""
        numPeopleWant = ""
    finally:
        return [numPeopleVisited, numPeopleWant]

def func_placeDesc(soup):
    placeDesc = []
    try: 
        placeDesc = " ".join(soup.find("div", {"class": "DDP__direction-copy"}).p.text.strip().split("\n"))
    except:
        print("placeDesc")
        placeDesc = ""
    finally:
        return placeDesc  

def func_placeShortDesc(soup):
    placeShortDesc = ""
    try: 
        placeShortDesc = soup.find("h3", {"class": "DDPage__header-dek"}).text.strip()
    except:
        print("placeShortDesc")
        placeShortDesc = ""
    finally:
        return placeShortDesc  

def func_placeNearby(soup):
    placeNearby = []
    try: 
        placeNearby = list(set([p.text for p in soup.find_all("div", {"class": "DDPageSiderailRecirc__item-title"})]))
    except:
        print("placeNearby")
        placeNearby = []
    finally:
        return placeNearby 

def func_placeAddress(soup):
    placeAddress = ""
    try: 
        address = soup.find("address", {"class": "DDPageSiderail__address"}).div
        address = " ".join(str(address).split("<div>")[1].strip().split("<br/>"))
        placeAddress = address
    except:
        print("placeAddress")
        placeAddress = ""
    finally:
        return placeAddress

def func_placeGeo(soup):
    placeAlt = "" 
    placeLong = ""
    try: 
        placeAlt, placeLong = [float(i) for i in soup.find("div", {"class": "DDPageSiderail__coordinates js-copy-coordinates"}).text.strip().split(", ")]
    except:
        print("placeAlt, placeLong")
        placeAlt = "" 
        placeLong = ""
    finally:
        return [placeAlt, placeLong]

def func_placeEditors(soup):
    placeEditors = []
    try:
        placeEditors = set()
        for i in soup.find_all("a", {"class": "DDPContributorsList__contributor"}):
            if i.span != None:
                placeEditors.add(str(i.span)[6:-7])
                # print(str(i.span)[6:-7])
        placeEditors = list(placeEditors)
    except:
        print("placeEditors")
        placeEditors = []
    finally:
        return placeEditors

def func_placePubDate(soup):
    placePubDate = ""
    try:
        date_raw = soup.find("div", {"class": "DDPContributor__name"}).text
        #print(date_raw)
        date_formatted = datetime.strptime(date_raw, '%B %d, %Y')
        placePubDate = date_formatted
    except:
        print("placePubDate")
        placePubDate = ""
    finally:
        return placePubDate

def func_placeRelatedLists(soup):
    placeRelatedLists = []
    try:
        placeRelatedLists = []
        for i in soup.find_all("a", {"data-gtm-content-type": "Place"}):
            placeRelatedLists.append(str(i.span)[6:-7].strip())
            # print(str(i.span)[6:-7])
    except:
        print("placeRelatedLists")
        placeRelatedLists = []
    finally:
        return placeRelatedLists

def func_placeRelatedPlaces(soup):
    placeRelatedPlaces = []
    try:
        placeRelatedPlaces = []
        for i in soup.find_all("a", {"data-gtm-content-type": "List"}):
            placeRelatedPlaces.append(str(i.span)[6:-7].strip())
            # print(str(i.span)[6:-7])
    except:
        print("placeRelatedPlaces")
        placeRelatedPlaces = []
    finally:
        return placeRelatedPlaces

def parse(filename, page):
    """
    description:
        parse file to Place object with defined fields
    params:
        - filename: name of file for parsing
        - page: current page
    return:
        Place object with parsed data
    """
    file_path = os.path.join(os.getcwd(), "places", str(page), filename)
    place = ""
    soup = ""
    with open(file_path, "r", encoding = "utf8") as fp:
        soup = BeautifulSoup(fp, 'html.parser')
    placeName = func_placeName(soup)
    placeTags = func_placeTags(soup)
    numPeopleVisited, numPeopleWant = func_numPeople(soup)
    placeDesc = func_placeDesc(soup)
    placeShortDesc = func_placeShortDesc(soup)
    placeNearby = func_placeNearby(soup)
    placeAddress = func_placeAddress(soup)
    placeAlt, placeLong = func_placeGeo(soup)
    placeEditors = func_placeEditors(soup)
    placePubDate = func_placePubDate(soup)
    placeRelatedLists = func_placeRelatedLists(soup)
    placeRelatedPlaces = func_placeRelatedPlaces(soup)
    placeURL = f"{root_url}/places/{filename[:-5]}"
    place = Place(placeName, 
                  placeTags, 
                  numPeopleVisited, 
                  numPeopleWant, 
                  placeDesc, 
                  placeShortDesc, 
                  placeNearby, 
                  placeAddress, 
                  placeAlt, 
                  placeLong, 
                  placeEditors, 
                  placePubDate,
                  placeRelatedLists,
                  placeRelatedPlaces,
                  placeURL)
    return place

def save_place_single_data(place, fp):
    """
    description:
        saves Place object to tsv file
    params:
        - place: Place object that has .to_string method to cast its data to string
        - fp: 'place_i.tsv' file that is opened for appending (writing) files
    """
    # write places data
    if place != None:
        fp.write(place.to_string()+"\n") 
    

def mean_grades(p):
    """
    This function computes the mean and rounds it by the second decimal.
    We use a function so that we can use it in the stud_fun function again.
    """
    total = 0
    i = 0
    if i < len(p):
        for t in p:
            total = total + int(p[i])
            i += 1
    mean = total / i
    return round(mean, 2)

def stud_fun(people, num_people):
    """
    What we do here is we create a new list (final_list) of lists (list_stud). 
    The nested lists are made by name and surname of the student and the
    mean of the grades.
    """
    final_list = []
    for x in range(1, int(num_people)+1):
        list_stud = []
        students = people[x].split()
        grades_list = students[2:]
        list_stud.append(students[0])
        list_stud.append(students[1])
        mean = mean_grades(grades_list)
        list_stud.append(mean)
        final_list.append(list_stud)
    return final_list

def insertionSort(arr):
    """
    description:
        insersion sort alghorithm 
    params:
        - arr: list with names and means of grades
    return:
        - computing time
        - sorted array
    """
    st = time.process_time()
    n = len(arr)
    for i in range(1, n):
        for j in range(i-1, -1, -1):
            if(arr[j][2] < arr[j+1][2]):
                arr[j], arr[j+1] = arr[j+1], arr[j]
            if(arr[j][2] == arr[j+1][2]):
                if(arr[j][0] > arr[j+1][0]):
                    arr[j], arr[j+1] = arr[j+1], arr[j]
                if(arr[j][0] == arr[j+1][0]):
                    if(arr[j][1] > arr[j+1][1]):
                        arr[j], arr[j+1] = arr[j+1], arr[j]
    et = time.process_time()
    ex_time = et - st
    return ex_time, arr

def par(array, low, high):
    pivot = array[high][2]
    i = low - 1
    for j in range(low, high):
        if array[j][2] > pivot:
            i = i + 1
            (array[i], array[j]) = (array[j], array[i])
        if array[j][2] == pivot:
            if array[j][0] == array[high][0]:
                if array[j][1] > array[high][1]:
                    i = i + 1
                    (array[i], array[j]) = (array[j], array[i])
            if array[j][0] < array[high][0]:
                i = i + 1
                (array[i], array[j]) = (array[j], array[i])
    (array[i+1], array[high]) = (array[high], array[i+1])
    return i + 1

def quickSort(array, low, high):
    """
    description:
        quick sort alghorithm 
    params:
        - array: list with names and means of grades
        - low: starting index
        - high: ending index
    return:
        - computing time
        - sorted array
    """
    st = time.process_time()
    if low < high:
        pi = par(array, low, high)
        quickSort(array, low, pi - 1)
        quickSort(array, pi + 1, high)
    et = time.process_time()
    ex_time = et - st
    return ex_time, array

def selectionSort(array, size):
    """
    description:
        selection sort alghorithm 
    params:
        - arr: list with names and means of grades
        - size: size of an arr
    return:
        - computing time
        - sorted array
    """
    st = time.process_time()
    for s in range(size):
        min_idx = s
        for i in range(s + 1, size):
            if array[i][2] > array[min_idx][2]:
                min_idx = i
            if array[i][2] == array[min_idx][2]:
                if array[i][0] == array[min_idx][0]:
                    if array[i][1] > array[min_idx][1]:
                        min_idx = i
                if array[i][0] < array[min_idx][0]:
                    min_idx = i            
        (array[s], array[min_idx]) = (array[min_idx], array[s])
    et = time.process_time()
    ex_time = et - st
    return ex_time, array