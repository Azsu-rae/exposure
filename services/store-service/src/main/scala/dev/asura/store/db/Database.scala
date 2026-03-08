package store.db

// This is just for testing. Consider using cats.effect.IOApp instead of calling
// unsafe methods directly.
import doobie.util.transactor.Transactor
import cats.effect.IO

object Database {
  def connect(): Transactor[IO] = {
    // A transactor that gets connections from java.sql.DriverManager and executes blocking operations
    // on an our synchronous EC. See the chapter on connection handling for more info.
    Transactor.fromDriverManager[IO](
      driver = "org.postgresql.Driver",
      url = "jdbc:postgresql:world",
      user = "postgres",
      pass = "password"
    )
  }
}
