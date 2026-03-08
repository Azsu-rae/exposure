name := "store-service"
version := "0.1.0"

scalaVersion := "3.8.2"
libraryDependencies ++= Seq(
  "org.tpolecat" %% "doobie-core" % "1.0.0-RC2",
  "org.tpolecat" %% "doobie-postgres" % "1.0.0-RC2",

  "de.huxhorn.sulky" % "de.huxhorn.sulky.ulid" % "8.3.0",
  "org.tpolecat" %% "doobie-hikari" % "1.0.0-RC2", // connection pool
  "org.postgresql" % "postgresql" % "42.6.0"
)
