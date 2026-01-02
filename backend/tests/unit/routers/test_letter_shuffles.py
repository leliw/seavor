from ampf.testing import ApiTestClient
from features.letter_shuffles.letter_shuffle_model import (
    LetterShuffleItem,
    LetterShuffleSet,
    LetterShuffleSetCreate,
    LetterShuffleSetHeader,
)

letter_shuffle_set = LetterShuffleSetCreate(
    title="Christmas",
    description="Words and phrases related to Christmas",
    items=[
        LetterShuffleItem(
            question="Carols",
            description="Traditional Christmas songs sung during the festive season.",
        ),
        LetterShuffleItem(
            question="Mistletoe",
            description="A plant hung as decoration, under which people traditionally kiss.",
        ),
        LetterShuffleItem(
            question="Snowman",
            description="A figure made of snow, typically with a carrot for a nose and coal for eyes.",
        ),
        LetterShuffleItem(
            question="Reindeer",
            description="Deer with large antlers, famous for pulling Santa's sleigh.",
        ),
        LetterShuffleItem(
            question="Gingerbread",
            description="A type of cookie or cake flavored with ginger, often made into festive shapes.",
        ),
        LetterShuffleItem(
            question="Eggnog",
            description="A rich, creamy, and sweet dairy-based beverage traditionally made with milk, cream, sugar, whipped eggs, and spirits.",
        ),
        LetterShuffleItem(
            question="Chimney",
            description="A vertical channel through which smoke and gases are carried up from a fire, famously used by Santa.",
        ),
        LetterShuffleItem(
            question="Sleigh",
            description="A vehicle on runners, used for traveling over snow or ice, often pulled by horses or reindeer.",
        ),
        LetterShuffleItem(
            question="Ornaments",
            description="Decorative items hung on a Christmas tree.",
        ),
        LetterShuffleItem(
            question="Candy Cane",
            description="A cane-shaped stick candy, often peppermint-flavored and striped red and white.",
        ),
    ],
)


def test_get_all(client: ApiTestClient):
    r = client.get_typed_list("/api/letter-shuffles", 200, LetterShuffleSetHeader)
    assert 0 == len(r)


def test_post_get_put_patch_delete(client: ApiTestClient):
    value = LetterShuffleSet.create(letter_shuffle_set)

    # POST
    p = client.post_typed("/api/letter-shuffles", 200, LetterShuffleSet, json=value)

    # GET ALL
    r = client.get_typed_list("/api/letter-shuffles", 200, LetterShuffleSetHeader)
    assert 1 == len(r)
    assert r[0].title == value.title

    # GET
    r = client.get_typed(f"/api/letter-shuffles/{p.id}", 200, LetterShuffleSet)
    assert r.title == value.title
    assert len(r.items) > 0
    assert isinstance(r.items[0].question_audio_file_name, str)


    # PUT
    p.title = "Updated title"
    client.put(f"/api/letter-shuffles/{p.id}", 200, json=p)
    r = client.get_typed(f"/api/letter-shuffles/{p.id}", 200, LetterShuffleSet)
    assert r.title == "Updated title"

    # PATCH
    p.title = "Patched title"
    client.patch(f"/api/letter-shuffles/{p.id}", 200, json=p)
    r = client.get_typed(f"/api/letter-shuffles/{p.id}", 200, LetterShuffleSet)
    assert r.title == "Patched title"

    # DELETE
    client.delete(f"/api/letter-shuffles/{p.id}", 200)
    client.get(f"/api/letter-shuffles/{p.id}", 404)
