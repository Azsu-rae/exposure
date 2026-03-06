
import de.huxhorn.sulky.ulid.ULID
import store.domain.Store


@main
def test() = {

  val ulid = new ULID()
  val store = Store.create(ulid.nextULID(), "Titanic", "Expensive coffee shop", ulid.nextULID())
  println(store)
}
