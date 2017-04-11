import java.util.ArrayList;
import java.util.List;

public class Botv11_2 {

    static int myID;
    static GameMap gameMap;
    static int DEPTH = 6;
    static double[][] recursiveValues;
    static int myArea;
    static boolean[][] isMine;
    static boolean[][] isStillMine;

    public static void main(String[] args) throws java.io.IOException {

        final InitPackage iPackage = Networking.getInit();
        myID = iPackage.myID;
        gameMap = iPackage.map;

        Networking.sendInit("Botv11_2 : NeutralBot");

        while(true) {
            List<Move> moves = new ArrayList<Move>();

            Networking.updateFrame(gameMap);

            // Initalize table of recursive values to avoid repeat computation
            recursiveValues = new double[gameMap.width][gameMap.height];
            for (int y = 0; y < gameMap.height; y++) {
                for (int x = 0; x < gameMap.width; x++) {
                    recursiveValues[x][y] = -1.0;
                }
            }

            //Find order to assign moves
            int[][] owners = new int[gameMap.width][gameMap.height];
            for (int y = 0; y < gameMap.height; y++) {
                for (int x = 0; x < gameMap.width; x++) {
                    Location loc = gameMap.getLocation(x, y);
                    owners[x][y] = loc.getSite().owner;
                }
            }

            List<List<Location>> borderDepths = new ArrayList<List<Location>>();
            myArea = getTotalArea();

            while (myArea > 0) {
                int[][] copyOwners = owners.clone();
                List<Location> locations = new ArrayList<Location>();
                for (int y = 0; y < gameMap.height; y++) {
                    for (int x = 0; x < gameMap.width; x++) {
                        Location loc = gameMap.getLocation(x, y);
                        if (owners[x][y] == myID
                                && isBorder(loc, copyOwners)) {
                            owners[x][y] = 0;
                            locations.add(loc);
                            myArea -= 1;
                        }
                    }
                }
                borderDepths.add(locations);
            }

            for (int i = borderDepths.size() - 1; i >= 0; i--) {
                for (Location location: borderDepths.get(i)) {
                    Site site = location.getSite();
                    moves.add(new Move(location, doMove(location, moves, i)));
                }
            }

            Networking.sendFrame(moves);
        }
    }

    static Direction doMove(Location loc, List<Move> moves, int borderDist) {
        Direction direction = findMove(loc, borderDist);
        Site current = loc.getSite();
        if (direction.equals(Direction.STILL) || direction == null) {
            return Direction.STILL;
        }
        Site destination = gameMap.getSite(loc, direction);
        int totalStrength = 0;
        if (current.strength > 1) {
            Location destLoc = gameMap.getLocation(loc, direction);
            totalStrength = current.strength;
            if (destination.owner == myID) {
                totalStrength += destination.strength;
            }
            for (Move move: moves) {
                if (move.loc.equals(destLoc)
                        && !move.dir.equals(Direction.STILL)) {
                    totalStrength -= destination.strength;
                }
                for (Direction test: Direction.CARDINALS) {
                    if (move.loc.equals(gameMap.getLocation(destLoc, test))
                            && opposites(move.dir, test)) {
                        totalStrength += gameMap.getSite(destLoc, test).strength;
                    }

                }
            }
            if ((totalStrength - 255) > 0.6 * current.strength) {
                return Direction.STILL;
            }
        }
        if (destination.owner != myID) {
            if (destination.strength >= totalStrength
                    && !(destination.strength == 255 && totalStrength >= 255)) {
                return Direction.STILL;
            }

        }
        if (destination.owner == myID && current.strength < 5 * current.production) {
            return Direction.STILL;
        }
        return direction;
    }

    static Direction findMove(Location loc, int borderDist) {
        Site mySite = loc.getSite();

        if (mySite.strength == 0) {
            return Direction.STILL;
        }

        Direction combatDirection = highDamage(loc);
        // Optimize combat
        if (combatDirection != null) {
            return combatDirection;
        }

        // Move in direction of best recursive outcome
        if (borderDist <= DEPTH) {
            Direction recDirection = recurseMoves(loc);
            if (recDirection != null) {
                if (gameMap.getSite(loc, recDirection).strength < mySite.strength) {
                    return recDirection;
                }
            }
        }

        // Dont move if weak
        if (mySite.strength < 5 * mySite.production) {
            return Direction.STILL;
        }

        // Else ove to border
        Direction targetDirection = borderDirections(loc);

        // Combine power with neighbor if possible
        if (borderDist <= DEPTH) {
            double maxValue = 0;
            double myValue = getRecursiveValue(loc);
            for (Direction direction: Direction.CARDINALS) {
                Location neighbor = gameMap.getLocation(loc, direction);
                double neighborValue = getRecursiveValue(neighbor);
                if (neighbor.getSite().owner == myID && neighborValue > myValue
                        && neighborValue > maxValue) {
                    targetDirection = direction;
                    maxValue = neighborValue;
                }
            }
        }

        return targetDirection;
    }

    static Direction recurseMoves(Location loc) {
        double[] values = new double[4];
        for (int i = 0; i < 4; i++) {
            Direction direction = Direction.CARDINALS[i];
            Location loc2 = gameMap.getLocation(loc, direction);
            int captures = 0;
            if (loc2.getSite().owner != myID) {
                values[i] = value(loc2);
                values[i] += getRecursiveValue(loc2);
            } else {
                values[i] = getRecursiveValue(loc2);
            }
        }
        int maxInd = maxIndex(values);
        if (values[maxInd] > 0) {
            return Direction.CARDINALS[maxInd];
        } else {
            return null;
        }

    }

    static double getRecursiveValue(Location loc) {
        int x = loc.x;
        int y = loc.y;
        if (recursiveValues[x][y] != - 1) {
            return recursiveValues[x][y];
        } else {
            double value = recursiveValue(loc, DEPTH, new ArrayList<Location>());
            recursiveValues[x][y] = value;
            return value;
        }
    }

    static double recursiveValue(Location loc, int depth, List<Location> visited) {
        if (depth <= 0) {
            return 0;
        }
        double[] values = new double[4];
        for (int i = 0; i < 4; i++) {
            Direction direction = Direction.CARDINALS[i];
            Location loc2 = gameMap.getLocation(loc, direction);
            boolean beenHere = false;
            for (Location visit: visited) {
                if (visit.equals(loc2) || beenHere) {
                    beenHere = true;
                }
            }
            if (beenHere) {
                values[i] = -42.0;
            }
            if (loc2.getSite().owner != myID && !beenHere) {
                values[i] = value(loc2);
                visited.add(loc2);
                values[i] += recursiveValue(loc2, depth - 1, visited);
                visited.remove(visited.size() - 1);
            } else if (!beenHere) {
                values[i] = recursiveValue(loc2, depth - 1, visited);
            }

        }
        int maxInd = maxIndex(values);
        return values[maxInd];
    }

    static Direction borderDirections(Location loc) {
        Location oLoc = loc;
        int minDist = 100000;
        Direction minDirection = Direction.STILL;
        for (int i = 0; i < 4; i++) {
            Direction direction = Direction.CARDINALS[i];
            loc = oLoc;
            int dist = 0;
            Site site = loc.getSite();
            while (site.owner == myID && dist < Math.max(gameMap.width,
                    gameMap.height) / 2) {
                loc = gameMap.getLocation(loc, direction);
                site = loc.getSite();
                dist += 1;
            }
            if (dist < minDist) {
                minDirection = direction;
                minDist = dist;
            }
        }
        return minDirection;
    }

    static Direction highDamage(Location loc) {
        Site mySite = loc.getSite();
        int maxDamage = 0;
        Direction maxDirection = null;
        for (Direction direction1: Direction.CARDINALS) {
            int myStrength = mySite.strength;
            int totalDamage = 0;
            if (isBuffer(gameMap.getLocation(loc, direction1))) {
                totalDamage -= myStrength;
            }
            if (gameMap.getSite(loc, direction1).owner != myID) {
                if (gameMap.getSite(loc, direction1).owner != 0) {
                    totalDamage += Math.min(gameMap.getSite(loc, direction1).strength,
                        myStrength);
                }
            }
            for (Direction direction2: Direction.CARDINALS) {
                Site site = gameMap.getSite(gameMap.getLocation(loc, direction1),
                    direction2);
                if (site.owner != myID && site.owner != 0 && myStrength > 0) {
                    totalDamage += Math.min(site.strength, myStrength);
                }
            }
            if (totalDamage > maxDamage) {
                maxDirection = direction1;
                maxDamage = totalDamage;
            }
        }
        return maxDirection;
    }

    static double value(Location loc) {
        Site site = loc.getSite();
        if (site.owner == myID) {
            return 0;
        } else {
            return (double) site.production / (site.strength + 1.0);
        }
    }

    static boolean opposites(Direction dir1, Direction dir2) {
        for (int i = 0; i < 4; i++) {
            if (dir1.equals(Direction.CARDINALS[i])
                    && dir2.equals(Direction.CARDINALS[(i+2) % 4])) {
                return true;
            }
        }
        return false;
    }

    static boolean isBorder(Location loc, int[][] owners) {
        for (Direction direction: Direction.CARDINALS) {
            int x = gameMap.getLocation(loc, direction).x;
            int y = gameMap.getLocation(loc, direction).y;
            if (owners[x][y] != myID) {
                return true;
            }
        }
        return false;
    }

    static int getTotalArea() {
        int totalArea = 0;
        for (int y = 0; y < gameMap.height; y++) {
            for (int x = 0; x < gameMap.width; x++) {
                Site aSite = gameMap.getLocation(x, y).getSite();
                if (aSite.owner == myID) {
                    totalArea += 1;
                }
            }
        }
        return totalArea;
    }

    static int maxIndex(double[] arrayVals) {
        double max = arrayVals[0];
        int maxInd = 0;
        for (int i = 1; i < arrayVals.length; i++) {
            if (arrayVals[i] > max) {
                max = arrayVals[i];
                maxInd = i;
            }
        }
        return maxInd;
    }

    static boolean isBuffer(Location loc) {
        if (loc.getSite().owner != 0 || loc.getSite().strength == 0) {
            return false;
        }
        for (int i = 0; i < 4; i++) {
            for (int j = i; j < i + 2; j++) {
                int k = j % 4;
                Direction dir1 = Direction.CARDINALS[i];
                Direction dir2 = Direction.CARDINALS[k];
                int owner = gameMap.getSite(gameMap.getLocation(loc, dir1),
                    dir2).owner;
                if (owner != 0 && owner != myID) {
                    return true;
                }
            }
        }
        return false;
    }

    static boolean[][] mySites() {
        boolean[][] mine = new boolean[gameMap.width][gameMap.height];
        for (int x = 0; x < gameMap.width; x++) {
            for (int y = 0; y < gameMap.height; y++) {
                int owner = gameMap.getLocation(x, y).getSite().owner;
                mine[x][y] = (owner == myID);
            }
        }
        return mine;
    }

}