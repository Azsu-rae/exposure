import store.domain.Store
import store.db.Database

import doobie._
import doobie.implicits._

import cats.effect.unsafe.implicits.global
import doobie.util.ExecutionContexts

import cats._
import cats.effect._
import cats.implicits._

def store_test() = {
  val store = Store.create(
    "Titanic",
    "Expensive coffee shop"
  )

  println()
  println(store)
  println()
}

def scala_test() = {

  val fruits = List("apple", "banana", "lime", "orange")

  val longFruits = for
    f <- fruits
    if f.length > 4
  yield f

  println(s"Before filtering: $fruits")
  println(s"After filtering: $longFruits")
}

def doobie_test() = {
  val program1 = 42.pure[ConnectionIO]
  val xa = Database.connect()
  val io = program1.transact(xa)
  println(io.unsafeRunSync())
  val program2 = sql"select 42".query[Int].unique
  val io2 = program2.transact(xa)
  println(io2.unsafeRunSync())
}

@main
def start() = {
  println()
  doobie_test()
  println()
}
