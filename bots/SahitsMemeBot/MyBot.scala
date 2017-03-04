//The improved version of the random bot on the site
//but its a meme
import scala.util.Random
object MyBot extends BotFactory {
  def main(args: Array[String]): Unit = {
    Runner.run("WhatWouldSimpkinsDo", this)
    var grid = Env.readInit()
  }

  override def make(id: Int): Bot = new MyBot(id)
}

class MyBot(myId: Int) extends Bot {
  override def getMoves(grid: Grid): Iterable[Move] = {
    var rand = Random
    val moves = Array(0, 1, 4)
    for {
      site <- grid.getMine(myId)
    } yield {
      for (neighbor <- grid.getNeighbors(site.location)) {
        if (neighbor.site.occupant.id != myId 
          && neighbor.site.occupant.strength < site.occupant.strength) {
          Move(site.location, neighbor.direction);
        }
      }
      if (site.occupant.strength < 5 * site.location.production) {
        Move(site.location, new Direction(0))
      } else {
        Move(site.location, new Direction(moves(rand.nextInt(3))))
      }
    }
  }
}
