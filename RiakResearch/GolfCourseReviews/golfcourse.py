import riak

def main():
    db = riak.RiakClient()
    course_bucket = db.bucket('golf_courses')
    golfers_bucket = db.bucket('golfers')
    while True:
        query = raw_input('Query the Database: ')
        print ""
        if query == 'commands' or query == 'help':
            printCommands() 
        elif query.startswith('addCourse'):
            firstSplit = query.split(',')
            firstArg = firstSplit[0].split('(')[1].strip()
            secondArg = firstSplit[1].strip()
            thirdArg = firstSplit[2].strip()
            lastArg = firstSplit[3].split(')')[0].strip()
            addCourse(db, firstArg, secondArg, thirdArg, lastArg)
        elif query.startswith('deleteCourse'):
            firstSplit = query.split(',')
            firstArgSplit = firstSplit[0].split('(')[1]
            firstArg = firstArgSplit.split(')')[0].strip()
            deleteCourse(db, firstArg)
        elif query.startswith('editCourseLocation'):
            firstSplit = query.split(',')
            firstArg = firstSplit[0].split('(')[1].strip()
            lastArg = firstSplit[1].split(')')[0].strip()
            editCourseLocation(db, firstArg, lastArg)
        elif query.startswith('editCourseName'):
            firstSplit = query.split(',')
            firstArg = firstSplit[0].split('(')[1].strip()
            lastArg = firstSplit[1].split(')')[0].strip()
            editCourseName(db, firstArg, lastArg)
        elif query.startswith('editCoursePar'):
            firstSplit = query.split(',')
            firstArg = firstSplit[0].split('(')[1].strip()
            lastArg = firstSplit[1].split(')')[0].strip()
            editCoursePar(db, firstArg, lastArg)
        elif query.startswith('searchByCourseID'):
            firstSplit = query.split(',')
            firstArgSplit = firstSplit[0].split('(')[1]
            firstArg = firstArgSplit.split(')')[0].strip()
            searchByCourseID(db, firstArg)
        elif query.startswith('searchByCourseName'):
            firstSplit = query.split(',')
            firstArgSplit = firstSplit[0].split('(')[1]
            firstArg = firstArgSplit.split(')')[0].strip()
            searchByCourseName(db, firstArg)
        elif query.startswith('searchByLocation'):
            firstSplit = query.split(',')
            firstArgSplit = firstSplit[0].split('(')[1]
            firstArg = firstArgSplit.split(')')[0].strip()
            searchByLocation(db, firstArg)
        elif query.startswith('searchByPar'):
            firstSplit = query.split(',')
            firstArgSplit = firstSplit[0].split('(')[1]
            firstArg = firstArgSplit.split(')')[0].strip()
            searchByPar(db, firstArg)
        elif query.startswith('addGolfer'):
            firstSplit = query.split(',')
            firstArg = firstSplit[0].split('(')[1].strip()
            secondArg = firstSplit[1].strip()
            lastArg = firstSplit[2].split(')')[0].strip()
            addBorrowerToLibrary(db, firstArg, secondArg, lastArg)
        elif query.startswith('deleteGolfer'):
            firstSplit = query.split(',')
            firstArgSplit = firstSplit[0].split('(')[1]
            firstArg = firstArgSplit.split(')')[0].strip()
            deleteGolfer(db, firstArg)
        elif query.startswith('editGolferName'):
            firstSplit = query.split(',')
            firstArg = firstSplit[0].split('(')[1].strip()
            lastArg = firstSplit[1].split(')')[0].strip()
            editGolferName(db, firstArg, lastArg)
        elif query.startswith('editGolferHomeCourse'):
            firstSplit = query.split(',')
            firstArg = firstSplit[0].split('(')[1].strip()
            lastArg = firstSplit[1].split(')')[0].strip()
            editGolferHomeCourse(db, firstArg, lastArg)
        elif query.startswith('searchByGolferName'):
            firstSplit = query.split(',')
            firstArgSplit = firstSplit[0].split('(')[1]
            firstArg = firstArgSplit.split(')')[0].strip()
            searchByGolferName(db, firstArg)
        elif query.startswith('searchByGolferUsername'):
            firstSplit = query.split(',')
            firstArgSplit = firstSplit[0].split('(')[1]
            firstArg = firstArgSplit.split(')')[0].strip()
            searchByGolferUsername(db, firstArg)
        elif query.startswith('searchByHomeCourse'):
            firstSplit = query.split(',')
            firstArgSplit = firstSplit[0].split('(')[1]
            firstArg = firstArgSplit.split(')')[0].strip()
            searchByHomeCourse(db, firstArg)
        elif query.startswith('addGolfCourseReview'):
            firstSplit = query.split(',')
            firstArg = firstSplit[0].split('(')[1].strip()
            lastArg = firstSplit[1].split(')')[0].strip()
            addGolfCourseReview(db, firstArg, lastArg)
        elif query.startswith('removeGolfCourseReview'):
            firstSplit = query.split(',')
            firstArg = firstSplit[0].split('(')[1].strip()
            lastArg = firstSplit[1].split(')')[0].strip()
            removeGolfCourseReview(db, firstArg, lastArg)
        elif query.startswith('sortByCourseName'):
            sortByCourseName(db)
        elif query.startswith('sortByPar'):
            sortByPar(db)
        elif query == 'q' or query == 'quit' or query == 'exit':
            break;
        else:
            print('Invalid command, if you need help, type help')

def addCourse(db, courseID, course_name, location, par):

def deleteCourse(db, courseID):

def editCourseLocation(db, courseID, location):

def editCourseName(db, courseID, courseName):

def editCoursePar(db, courseID, par):

def searchByCourseID(db, courseID):

def searchByCourseName(db, course_name):

def searchByLocation(db, location):

def searchByPar(db, par):

def addGolfer(db, username, name, homeCourseID):

def deleteGolfer(db, username):

def editGolferName(db, username, name):

def editGolferHomeCourse(db, username, homeCourseID):

def searchByGolferName(db, name):

def searchByHomeCourse(db, homeCourseID):

def addGolfCourseReview(db, username, courseID):

def removeGolfCourseReview(db, username, courseID):

def sortByCourseName(db):

def sortByPar(db):

def printCommands():
    print('addCourse(courseID, courseName, location, par)')
    print('deleteCourse(courseID)')
    print('editCourseLocation(courseID, location)')
    print('editCourseName(courseID, courseName)')
    print('editCoursePar(courseID, par)')
    print('searchByCourseID(courseID)')
    print('searchByCourseName(courseName)')
    print('searchByLocation(location)')
    print('searchByPar(par)')
    print('addGolfer(username, name, homeCourseID)')
    print('deleteGolfer(username)')
    print('editGolferName(username, name)')
    print('editGolferHomeCourse(username, homeCourseID)')
    print('searchByGolferName(name)')
    print('searchByGolferUsername(username)')
    print('searchByHomeCourse(homeCourseID)')
    print('addGolfCourseReview(username, courseID)')
    print('removeGolfCourseReview(username, courseID)')
    print('sortByCourseName()')
    print('sortByPar()')
    print ""  

if __name__ == '__main__':
    main()