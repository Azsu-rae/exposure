import de.huxhorn.sulky.ulid.ULID

@main
def store() = {
  val ulid = new ULID()
  val id = ulid.nextULID()

  println(id)
}
