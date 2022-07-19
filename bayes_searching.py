import sys
import random
import itertools
import numpy as np
import cv2

# the map's picture
map = "cape.png"

# the coordinate of searching areas
SA1_CORNERS = (130, 265,180, 315)
SA2_CORNERS = (80, 255, 130, 305)
SA3_CORNERS = (105, 205, 155, 255)

class Search():
    def __init__(self):
        # load gray cascade picture, then change into BGR picture
        self.img = cv2.imread(map, cv2.IMREAD_COLOR)
        if self.img is None:
            print(f"Couldn't load map file{map}.")
            sys.exit(1)
        # record searching area's number
        self.area_actual = 0
        # record the sailor's coordinate after searched
        self.sailor_actual = [0, 0]

        # record searching areas' coordinate
        self.sa1 = self.img[SA1_CORNERS[1]: SA1_CORNERS[3], SA1_CORNERS[0]: SA1_CORNERS[2]]
        self.sa2 = self.img[SA2_CORNERS[1]: SA2_CORNERS[3], SA2_CORNERS[0]: SA2_CORNERS[2]]
        self.sa3 = self.img[SA3_CORNERS[1]: SA3_CORNERS[3], SA3_CORNERS[0]: SA3_CORNERS[2]]

        # the probability of searching the sailor in every areas    
        self.p1 = 0.2
        self.p2 = 0.5
        self.p3 = 0.3

        # the searching effectivness probabilities of every areas
        self.sep1 = 0
        self.sep2 = 0
        self.sep3 = 0

    def draw_map(self, last_known):
        # draw the scale
        cv2.line(self.img, (20, 370), (70, 370), (0, 0, 0), 2)
        cv2.putText(self.img, "0", (8, 370), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0))
        cv2.putText(self.img, "50 Nautical Miles", (71, 370), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0))

        # draw the searching areas
        cv2.rectangle(self.img, (SA1_CORNERS[0], SA1_CORNERS[1]), (SA1_CORNERS[2], SA1_CORNERS[3]), (0, 0, 0), 1)
        cv2.putText(self.img, "1", (SA1_CORNERS[0] + 3, SA1_CORNERS[1] + 15), cv2.FONT_HERSHEY_PLAIN, 1, 0)
        cv2.rectangle(self.img, (SA2_CORNERS[0], SA2_CORNERS[1]), (SA2_CORNERS[2], SA2_CORNERS[3]), (0, 0, 0), 1)
        cv2.putText(self.img, "2", (SA2_CORNERS[0] + 3, SA2_CORNERS[1] + 15), cv2.FONT_HERSHEY_PLAIN, 1, 0)
        cv2.rectangle(self.img, (SA3_CORNERS[0], SA3_CORNERS[1]), (SA3_CORNERS[2], SA3_CORNERS[3]), (0, 0, 0), 1)
        cv2.putText(self.img, "3", (SA3_CORNERS[0] + 3, SA3_CORNERS[1] + 15), cv2.FONT_HERSHEY_PLAIN, 1, 0)

        # label the final position of the sailor
        cv2.putText(self.img, "+", (last_known), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255))

        # add explanation
        cv2.putText(self.img, "+ = Last Known Position", (274, 355), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255))
        cv2.putText(self.img, "* = Actucal Position", (275, 370), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0))

        # display the image
        cv2.imshow("Search Area", self.img)
        cv2.moveWindow("Search Area", 750, 10)
        cv2.waitKey(5000)
        cv2.destroyAllWindows()

    def sailor_final_location(self, num_search_areas):
        # search randomly in searching area(the three searching areas are in same size)
        self.sailor_actual[0] = np.random.choice(self.sa1.shape[1], 1)
        self.sailor_actual[1] = np.random.choice(self.sa1.shape[0], 1)

        # use traingular distribution to decide the searching area
        area = int(random.triangular(1, num_search_areas + 1))

        # return the searching coordinate
        if area == 1:
            x = self.sailor_actual[0] + SA1_CORNERS[0]
            y = self.sailor_actual[1] + SA1_CORNERS[1]
            self.area_actual = 1
        elif area == 2:
            x = self.sailor_actual[0] + SA2_CORNERS[0]
            y = self.sailor_actual[1] + SA2_CORNERS[1]
            self.area_actual = 2
        elif area == 3:
            x = self.sailor_actual[0] + SA3_CORNERS[0]
            y = self.sailor_actual[1] + SA3_CORNERS[1]
            self.area_actual = 3
        return x[0], y[0]

    # set the searching effectiveness probabilities of every searching areas
    def calc_search_effectiveness(self):
        self.sep1 = random.uniform(0.2, 0.9)
        self.sep2 = random.uniform(0.2, 0.9)
        self.sep3 = random.uniform(0.2, 0.9)
    
    def conduct_search(self, area_num, area_array, effectiveness_prob):
        # iterate every corners of the searching area
        local_y_range = range(area_array.shape[0])
        local_x_range = range(area_array.shape[1])
        coords = list(itertools.product(local_x_range, local_y_range))

        # keep the effectiveness percentage
        random.shuffle(coords)
        coords = coords[: int(len(coords) * effectiveness_prob)]
        local_actual = (self.sailor_actual[0], self.sailor_actual[1])

        # check whether find th sailor
        if area_num == self.area_actual and local_actual in coords:
            return f"Found in Area {area_num}.", coords
        else:
            return "Not found", coords

    # update new prbabilities of searching the sailor in certain searching area
    def revise_target_probs(self):
        denom = self.p1 * (1 - self.sep1) + self.p2 * (1 - self.sep2) + self.p3 * (1 - self.sep3)
        self.p1 = self.p1 * (1 - self.sep1) / denom
        self.p2 = self.p2 * (1 - self.sep2) / denom
        self.p3 = self.p3 * (1 - self.sep3) / denom

# display the menu of searching option
def draw_menu(search_num):
    print(f"\nSearch {search_num}")
    print("""
        Choose next areas to search:
        0 - Quit
        1 - Search Area 1 twice
        2 - Search Area 2 twice
        3 - Search Area 3 twice
        4 - Search Area 1 & 2
        5 - Search Area 1 & 3
        6 - Search Area 2 & 3
        7 - Start over""")

def main():
    app = Search()
    app.draw_map((160, 290))
    # set the sailor's actual position
    sailor_x, sailor_y = app.sailor_final_location(3)

    # display the initial probabilities
    print("-" * 65)
    print("\nInitial Target(P) Probabilities:")
    print("P1 = {:.3f}, P2 = {:.3f}, P3 = {:.3f}".format(app.p1, app.p2, app.p3))
    
    search_num = 1
    while True:
        # set searching effectiveness probabilities
        app.calc_search_effectiveness()
        # display searching options
        draw_menu(search_num)
        choice = input("Choice:")
        if choice == "0":
            sys.exit()
        elif choice == "1":
            result1, coords1 = app.conduct_search(1, app.sa1, app.sep1)
            result2, coords2 = app.conduct_search(1, app.sa1, app.sep1)
            app.sep1 = len(set(coords1 + coords2)) / len(app.sa1) ** 2
            app.sep2 = 0
            app.sep3 = 0
        elif choice == "2":
            result1, coords1 = app.conduct_search(2, app.sa2, app.sep2)
            result2, coords2 = app.conduct_search(2, app.sa2, app.sep2)
            app.sep1 = 0
            app.sep2 = len(set(coords1 + coords2)) / len(app.sa2) ** 2
            app.sep3 = 0
        elif choice == "3":
            result1, coords1 = app.conduct_search(1, app.sa3, app.sep3)
            result2, coords2 = app.conduct_search(1, app.sa3, app.sep3)
            app.sep1 = 0
            app.sep2 = 0
            app.sep3 = len(set(coords1 + coords2)) / len(app.sa3) ** 2
        elif choice == "4":
            result1, coords1 = app.conduct_search(1, app.sa1, app.sep1)
            result2, coords2 = app.conduct_search(2, app.sa2, app.sep2)
            app.sep3 = 0
        elif choice == "5":
            result1, coords1 = app.conduct_search(1, app.sa1, app.sep1)
            result2, coords2 = app.conduct_search(3, app.sa3, app.sep3)
            app.sep2 = 0
        elif choice == "6":
            result1, coords1 = app.conduct_search(2, app.sa2, app.sep2)
            result2, coords2 = app.conduct_search(3, app.sa3, app.sep3)
            app.sep1 = 0
        elif choice == "7":
            main()
        else:
            print("\nIt's not a valid choice.")
            continue
        
        # update new searching probabilities
        app.revise_target_probs()
        print(f"\nSearch {search_num} Result 1 = {result1}")
        print(f"Search {search_num} Result 2 = {result2}")
        print(f"Search {search_num} Effectiveness (E):")
        print("E1 = {:.3f}, E2 = {:.3f}, E3 = {:.3f}".format(app.sep1, app.sep2, app.sep3))

        # display searching result
        if result1 == "Not found" and result2 == "Not found":
            print(f"\nNew Target Probabilities(P) for Search{search_num +1}")
            print("P1 = {:.3f}, P2 = {:.3f}, P3 = {:.3f}".format(app.p1, app.p2, app.p3))
        else:
            cv2.circle(app.img, (sailor_x, sailor_y), 3, (255, 0, 0), -1)
            cv2.imshow("Search Area", app.img)
            cv2.waitKey(5000)
            cv2.destroyAllWindows()
            break
        search_num += 1

if __name__ == "__main__":
    main()