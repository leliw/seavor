from ampf.testing import ApiTestClient
from features.letter_shuffles.letter_shuffle_model import (
    LetterShuffleItem,
    LetterShuffleSet,
    LetterShuffleSetCreate,
    LetterShuffleSetHeader,
)

letter_shuffle_set = LetterShuffleSetCreate(
    target_language_code="en",
    target_title="Christmas",
    target_description="Words and phrases related to Christmas",
    items=[
        LetterShuffleItem(
            target_phrase="Carols",
            target_description="Traditional Christmas songs sung during the festive season.",
        ),
        LetterShuffleItem(
            target_phrase="Mistletoe",
            target_description="A plant hung as decoration, under which people traditionally kiss.",
        ),
        LetterShuffleItem(
            target_phrase="Snowman",
            target_description="A figure made of snow, typically with a carrot for a nose and coal for eyes.",
        ),
        LetterShuffleItem(
            target_phrase="Reindeer",
            target_description="Deer with large antlers, famous for pulling Santa's sleigh.",
        ),
        LetterShuffleItem(
            target_phrase="Gingerbread",
            target_description="A type of cookie or cake flavored with ginger, often made into festive shapes.",
        ),
        LetterShuffleItem(
            target_phrase="Eggnog",
            target_description="A rich, creamy, and sweet dairy-based beverage traditionally made with milk, cream, sugar, whipped eggs, and spirits.",
        ),
        LetterShuffleItem(
            target_phrase="Chimney",
            target_description="A vertical channel through which smoke and gases are carried up from a fire, famously used by Santa.",
        ),
        LetterShuffleItem(
            target_phrase="Sleigh",
            target_description="A vehicle on runners, used for traveling over snow or ice, often pulled by horses or reindeer.",
        ),
        LetterShuffleItem(
            target_phrase="Ornaments",
            target_description="Decorative items hung on a Christmas tree.",
        ),
        LetterShuffleItem(
            target_phrase="Candy Cane",
            target_description="A cane-shaped stick candy, often peppermint-flavored and striped red and white.",
        ),
    ],
)

endpoint = "/api/target-languages/en/letter-shuffles"
def test_get_all(client: ApiTestClient):
    r = client.get_typed_list(endpoint, 200, LetterShuffleSetHeader)
    assert 0 == len(r)


def test_post_get_put_patch_delete(client: ApiTestClient):
    value = LetterShuffleSet.create(letter_shuffle_set)

    # POST
    p = client.post_typed(endpoint, 200, LetterShuffleSet, json=value)

    # GET ALL
    r = client.get_typed_list(endpoint, 200, LetterShuffleSetHeader)
    assert 1 == len(r)
    assert r[0].target_title == value.target_title

    # GET
    r = client.get_typed(f"{endpoint}/{p.id}", 200, LetterShuffleSet)
    assert r.target_title == value.target_title
    assert len(r.items) > 0
    assert isinstance(r.items[0].target_phrase_audio_file_name, str)


    # PUT
    p.target_title = "Updated title"
    client.put(f"{endpoint}/{p.id}", 200, json=p)
    r = client.get_typed(f"{endpoint}/{p.id}", 200, LetterShuffleSet)
    assert r.target_title == "Updated title"

    # PATCH
    p.target_title = "Patched title"
    client.patch(f"{endpoint}/{p.id}", 200, json=p)
    r = client.get_typed(f"{endpoint}/{p.id}", 200, LetterShuffleSet)
    assert r.target_title == "Patched title"

    # DELETE
    client.delete(f"{endpoint}/{p.id}", 200)
    client.get(f"{endpoint}/{p.id}", 404)
