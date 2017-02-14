#include <stdlib.h>
#include <time.h>
#include <cstdlib>
#include <ctime>
#include <time.h>
#include <set>
#include <fstream>

#include "hlt.hpp"
#include "networking.hpp"

hlt::GameMap presentMap;
unsigned char myID;
int turn;

int findNearestEnemyDirection(hlt::Location loc) {
    unsigned char direction = NORTH;
    int maxDistance = presentMap.width / 2;
    int maxSearch = presentMap.width / 2;
    for (int d = 0; d < 5; d++) {
        int distance = 0;
        hlt::Location current = loc;
        hlt::Site site = presentMap.getSite(current, d);
        while (site.owner == myID && distance < maxDistance) {
            distance ++;
            current = presentMap.getLocation(current, d);
            site = presentMap.getSite(current);
        }

        float priority = 0;
        float away = 2;
        int travelled = 0;
        while (site.owner != myID && travelled < maxSearch) {
            travelled++;
            away = away * away;
            if (site.owner == 0) {
                priority -= (site.strength) / away;
            } else if (travelled < 1){
                priority += (site.strength) / away;
            }
            priority += (site.production) / away;
            current = presentMap.getLocation(current, d);
            site = presentMap.getSite(current);
        }

        priority = priority / 5;
        distance = distance - priority;

        if (distance < maxDistance) {
            direction = d;
            maxDistance = distance;
        }


    }
    return direction;
}

// int maxDir(int dir[5]) {
//     int max = 0;
//     for (int i = 0; i < 5; i ++) {
//         if (dir[i] > dir[max]) {
//             max = i;
//         }
//     }
//     return max;
// }

int priority(hlt::Site site) {
    return site.production - site.strength / 5;
}

int calcDamage(hlt::Location location) {
    int damage = 0;
    for (int i = 0; i < 5; i++) {
        if (presentMap.getSite(location, i).owner != 0
            && presentMap.getSite(location, i).owner != myID)
            damage += presentMap.getSite(location).strength;
    }
    return damage;
}

unsigned char assign_move(hlt::GameMap presentMap,
        unsigned char myID, unsigned short b, unsigned short a) {
    hlt::Site site = presentMap.getSite({ b, a });
    hlt::Location location;
    location.x = b;
    location.y = a;
    bool outer = false;
    unsigned char leastResistance = 0;
    int damage = 0;
    for (int j = 0; j < 5; j++) {
        if (presentMap.getSite(location, j).owner == 0) {
            if (leastResistance == 0) {
                leastResistance = j;
            } else {
                //expansion algorithm
                if (priority(presentMap.getSite(location, leastResistance))
                    < priority(presentMap.getSite(location, j))) {
                    damage = priority(presentMap.getSite(location, j));
                    leastResistance = j;
                }

                //combat algorithm
                if (calcDamage(presentMap.getLocation(location, j)) > 0) {
                    if (damage < calcDamage(presentMap.getLocation(location, j))) {
                        damage = calcDamage(presentMap.getLocation(location, j));
                        leastResistance = j;
                    }
                }

                //conquer algorithm

            }
            outer = true;
        }
    }


    // int damage = 0;

    // for (int j = 0; j < 5; j++) {
    //     if (presentMap.getSite(location, j).owner != myID) {
    //         if (leastResistance == 0) {
    //             leastResistance = j;
    //         } else {
    //             if (resistance(presentMap.getSite(location, leastResistance))
    //                 > resistance(presentMap.getSite(location, j))) {
    //                 leastResistance = j;
    //             }
    //         }
    //         outer = true;
    //     }
    // }

    unsigned char move;
    if (outer == false) {
        if (site.strength < 5 * site.production) {
            move = STILL;
        } else {
            move = findNearestEnemyDirection(location);

            // if (site.strength
            //     + presentMap.getSite(location, move).strength > 255) {
            //     move = STILL;
            // }
        }
    } else {
        if (presentMap.getSite(location, leastResistance).strength >= site.strength) {
            move = STILL;
        } else {
            move = leastResistance;
        }
    }
    return move;
}


int main() {
    srand(time(NULL));

    std::cout.sync_with_stdio(0);
    getInit(myID, presentMap);
    sendInit("MyC++Bot");

    std::set<hlt::Move> moves;

    while(true) {
        moves.clear();

        getFrame(presentMap);

        for(unsigned short a = 0; a < presentMap.height; a++) {
            for(unsigned short b = 0; b < presentMap.width; b++) {
                if (presentMap.getSite({ b, a }).owner == myID) {
                    moves.insert({ { b, a }, assign_move(presentMap, myID, b, a)});
                }
            }
        }
        turn++;
        sendFrame(moves);
    }

    return 0;
}
