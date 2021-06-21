import numpy as np
import operator
import sys


# signup score and library. We have to sort based on signup score, and hence item getter(0) since based on array1 we are sorting
def parallel_sort(array_1, array_2, ascending=False):
    if not ascending:
        return zip(*sorted(zip(array_1, array_2), key=operator.itemgetter(0))[::-1])
    return zip(*sorted(zip(array_1, array_2), key=operator.itemgetter(0)))
# zip is to create two arrays such that their keys are matching.

class Library:

    def __init__(self, id, book_ids, signup_days, max_books_scanned_per_day):
        self.id = id
        self.book_ids = book_ids
        self.signup_days = signup_days
        self.max_books_scanned_per_day = max_books_scanned_per_day

    def get_best_book_ids(self, start_day=0):
        global book_scores, libraries_signup_days, libraries_max_books_scanned_per_day, D, final_books
        available_days = D - self.signup_days - start_day
        #start day is different for different libraries, and available days also depends on previous libraries which had been there before.

        available_books = list(set(self.book_ids) - set(final_books))
        current_book_scores = np.take(book_scores, available_books)
        # returns array of same type with all the values of given indices. So here np.take will return an array which contains
        # book scores of all available books

        max_num_books = max(min(int(available_days * self.max_books_scanned_per_day), len(available_books)), 0)
        # if available books is 1 and max scan possible is 2 then we have to scan 1 only hence the min thing.

        if max_num_books == 0:
            return []

        # get top k books (k=max_num_books)
        ind = np.argpartition(current_book_scores, -max_num_books)[-max_num_books:]
        # argpartition returns the array with index of the books in sorted order, and we have passed all values here

        return np.take(available_books, ind)

    def get_best_books_score(self, start_day=0):
        global book_scores, libraries_signup_days, libraries_max_books_scanned_per_day, D
        available_days = D - self.signup_days - start_day
        max_num_books = max(min(int(available_days * self.max_books_scanned_per_day), len(self.book_ids)), 0)

        current_book_scores = np.take(book_scores, self.book_ids)

        # get top k books (k=max_num_books) argpartition returns the sorted index of all books since all values till max books #are passed one by one
        ind = np.argpartition(current_book_scores, -max_num_books)[-max_num_books:]
        best_books_scores = np.take(current_book_scores, ind)

        return np.sum(best_books_scores)

    # returns string representation of object
    def __repr__(self):
        return self.id.__str__()


# sum of book scores of all book id's passed
def sum_book_scores(book_ids):
    global book_scores
    return np.sum(np.take(book_scores, list(book_ids)))


files = [
    "a_example"]  # , "b_read_on", "c_incunabula", "d_tough_choices", "e_so_many_books", "f_libraries_of_the_world"]

total_score = 0

for file in files:

    with open("inputs/" + file + ".txt", "r") as f:
        content = f.read().splitlines()  # read each input lines differently
    print(file)  # prints the file name

    for z in range(60):
        print("*-*", end='')
    print("\n\t\t\t\t\t\t\t\t\t\t\t\tEnter the number of Books,Libraries,Days: ")
    B, L, D = list(map(int, content[0].split(' ')))
    print("\t\t\t\t\t\t\t\t\t\t\t\t", B, "\t", L, "\t ", D)
    print("\t\t\t\t\t\t\t\t\t\t\t\tEnter the Book scores: ", end='')
    book_scores = list(map(int, content[1].split(' ')))
    for x in range(len(book_scores)):
        print(book_scores[x], end=" ")
    print("")
    pos = 1
    # library attributes : hence size of all below parameters are L
    libraries_num_books = np.zeros(L)  # number of books in lib 0,1,2 etc hence array of size L
    libraries_signup_days = np.zeros(L)  # signup days for the libraries hence array of size L
    libraries_max_books_scanned_per_day = np.zeros(L)  # max books canned per day for the libraries

    libraries = np.empty(L, dtype=Library)  # array number of elements in row is L and data type is library
    for i in range(L):
        print("\n\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t-*********** Library", i, "**********-",
              " \n\t\t\t\t\t\t\t\t\t\t\t\tBooks \t Signup days \t Books shipped per day ")
        pos += 1
        n, t, m = list(map(int, content[pos].split(' ')))
        libraries_num_books[i] = n
        libraries_signup_days[i] = t
        libraries_max_books_scanned_per_day[i] = m
        print("\t\t\t\t\t\t\t\t\t\t\t\t", n, "\t\t\t", t, "\t\t\t\t\t", m)
        pos += 1
        print("\n\t\t\t\t\t\t\t\t\t\t\t\tEnter Book ids :", end='')

        book_ids = np.asarray(list(map(int, content[pos].split(' '))))
        for x in range(len(book_ids)):
            print("\t", book_ids[x], end=" ")

        libraries[i] = Library(i, book_ids, t, m)

    # Vectorization is used to speed up the Python code without using loop.
    # Using such a function can help in minimizing the running time of code efficiently.
    library_book_score_counter = np.vectorize(lambda library: library.get_best_books_score())
    libraries_scores = library_book_score_counter(libraries)
# library_book_score_counter counts the score of the libraries,
# we pass the array libraries and vectorize takes in each element of the array passed and gets the best book score
# for it.The result is stored in libraries_scores
    heuristic_score = np.vectorize(lambda book_score, signup_days: book_score / signup_days)
    signup_scores = heuristic_score(libraries_scores, libraries_signup_days)

    signup_scores, libraries_sorted = parallel_sort(signup_scores, libraries)

    final_books = set()
    with open(
            "outputs/" + file + ".out", 'w+') as f:

        f.write(str(L) + "\n")
        print()
        for z in range(60):
            print("*-*", end='')

        print('\n\n\t\t\t\t\t\t\t\t\t\t\t\tNumber of libraries scanned up for signing = ', str(L))
        start_day = 0
        for i in range(L):

            current_library = libraries_sorted[i]
            chosen_book_ids = current_library.get_best_book_ids(start_day)
            final_books.update(chosen_book_ids)
            start_day += current_library.signup_days

            if len(chosen_book_ids) > 0:
                f.write(str(current_library.id) + " " + str(len(chosen_book_ids)) + "\n")
                f.write(str(' '.join(map(str, chosen_book_ids))) + "\n")
            # print(str(current_library.id) + " " + str(len(chosen_book_ids))
            else:
                f.write(str(current_library.id) + " 1\n")
                f.write(str(current_library.book_ids[0]) + "\n")

            if len(chosen_book_ids) > 0:
                print("\n\t\t\t\t\t\t\t\t\t\t\t\tLibrary chosen \t\t\t\t\t   Number of books scanned from library\n")
                print(" \t\t\t\t\t\t\t\t\t\t\t\t\t\t",
                      str(current_library.id) + " \t\t\t\t\t\t\t\t\t\t" + str(len(chosen_book_ids)) + "\n")
                print("\t\t\t\t\t\t\t\t\t\t\t\tBook ID's of books chosen from library :", end=" ")
                print(str(' '.join(map(str, chosen_book_ids))))
            # print(str(current_library.id) + " " + str(len(chosen_book_ids))

            else:
                print(str(current_library.id) + " 1\n")
                print(str(current_library.book_ids[0]) + "\n")

            # progress = 100 * i / (2 * L)
            # sys.stdout.write("\rCreating output... (" + str(int(progress)) + " %)")

        score = sum_book_scores(final_books)
        total_score += score

        # print("\r- Score:", score)

print("")
print("\n\t\t\t\t\t\t\t\t\t\t\t\tTotal score:", total_score, "\n\n")

for z in range(60):
    print("*-*", end='')
