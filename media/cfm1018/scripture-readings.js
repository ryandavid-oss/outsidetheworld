(() => {
  'use strict';
  // King James Version text; verse wording is retained without study-note markers.
  const chapters = {
  "ot/isa/61": [
    {
      "number": 1,
      "text": "The Spirit of the Lord GOD is upon me; because the LORD hath anointed me to preach good tidings unto the meek; he hath sent me to bind up the brokenhearted, to proclaim liberty to the captives, and the opening of the prison to them that are bound;"
    },
    {
      "number": 2,
      "text": "To proclaim the acceptable year of the LORD, and the day of vengeance of our God; to comfort all that mourn;"
    },
    {
      "number": 3,
      "text": "To appoint unto them that mourn in Zion, to give unto them beauty for ashes, the oil of joy for mourning, the garment of praise for the spirit of heaviness; that they might be called trees of righteousness, the planting of the LORD, that he might be glorified."
    }
  ],
  "nt/luke/4": [
    {
      "number": 16,
      "text": "And he came to Nazareth, where he had been brought up: and, as his custom was, he went into the synagogue on the sabbath day, and stood up for to read."
    },
    {
      "number": 17,
      "text": "And there was delivered unto him the book of the prophet Esaias. And when he had opened the book, he found the place where it was written,"
    },
    {
      "number": 18,
      "text": "The Spirit of the Lord is upon me, because he hath anointed me to preach the gospel to the poor; he hath sent me to heal the brokenhearted, to preach deliverance to the captives, and recovering of sight to the blind, to set at liberty them that are bruised,"
    },
    {
      "number": 19,
      "text": "To preach the acceptable year of the Lord."
    },
    {
      "number": 20,
      "text": "And he closed the book, and he gave it again to the minister, and sat down. And the eyes of all them that were in the synagogue were fastened on him."
    },
    {
      "number": 21,
      "text": "And he began to say unto them, This day is this scripture fulfilled in your ears."
    },
    {
      "number": 22,
      "text": "And all bare him witness, and wondered at the gracious words which proceeded out of his mouth. And they said, Is not this Joseph’s son?"
    },
    {
      "number": 23,
      "text": "And he said unto them, Ye will surely say unto me this proverb, Physician, heal thyself: whatsoever we have heard done in Capernaum, do also here in thy country."
    },
    {
      "number": 24,
      "text": "And he said, Verily I say unto you, No prophet is accepted in his own country."
    },
    {
      "number": 25,
      "text": "But I tell you of a truth, many widows were in Israel in the days of Elias, when the heaven was shut up three years and six months, when great famine was throughout all the land;"
    },
    {
      "number": 26,
      "text": "But unto none of them was Elias sent, save unto Sarepta, a city of Sidon, unto a woman that was a widow."
    },
    {
      "number": 27,
      "text": "And many lepers were in Israel in the time of Eliseus the prophet; and none of them was cleansed, saving Naaman the Syrian."
    },
    {
      "number": 28,
      "text": "And all they in the synagogue, when they heard these things, were filled with wrath,"
    },
    {
      "number": 29,
      "text": "And rose up, and thrust him out of the city, and led him unto the brow of the hill whereon their city was built, that they might cast him down headlong."
    },
    {
      "number": 30,
      "text": "But he passing through the midst of them went his way,"
    }
  ],
  "ot/1-kgs/17": [
    {
      "number": 8,
      "text": "And the word of the LORD came unto him, saying,"
    },
    {
      "number": 9,
      "text": "Arise, get thee to Zarephath, which belongeth to Zidon, and dwell there: behold, I have commanded a widow woman there to sustain thee."
    },
    {
      "number": 10,
      "text": "So he arose and went to Zarephath. And when he came to the gate of the city, behold, the widow woman was there gathering of sticks: and he called to her, and said, Fetch me, I pray thee, a little water in a vessel, that I may drink."
    },
    {
      "number": 11,
      "text": "And as she was going to fetch it, he called to her, and said, Bring me, I pray thee, a morsel of bread in thine hand."
    },
    {
      "number": 12,
      "text": "And she said, As the LORD thy God liveth, I have not a cake, but an handful of meal in a barrel, and a little oil in a cruse: and, behold, I am gathering two sticks, that I may go in and dress it for me and my son, that we may eat it, and die."
    },
    {
      "number": 13,
      "text": "And Elijah said unto her, Fear not; go and do as thou hast said: but make me thereof a little cake first, and bring it unto me, and after make for thee and for thy son."
    },
    {
      "number": 14,
      "text": "For thus saith the LORD God of Israel, The barrel of meal shall not waste, neither shall the cruse of oil fail, until the day that the LORD sendeth rain upon the earth."
    },
    {
      "number": 15,
      "text": "And she went and did according to the saying of Elijah: and she, and he, and her house, did eat many days."
    },
    {
      "number": 16,
      "text": "And the barrel of meal wasted not, neither did the cruse of oil fail, according to the word of the LORD, which he spake by Elijah."
    }
  ],
  "ot/2-kgs/5": [
    {
      "number": 1,
      "text": "Now Naaman, captain of the host of the king of Syria, was a great man with his master, and honourable, because by him the LORD had given deliverance unto Syria: he was also a mighty man in valour, but he was a leper."
    },
    {
      "number": 2,
      "text": "And the Syrians had gone out by companies, and had brought away captive out of the land of Israel a little maid; and she waited on Naaman’s wife."
    },
    {
      "number": 3,
      "text": "And she said unto her mistress, Would God my lord were with the prophet that is in Samaria! for he would recover him of his leprosy."
    },
    {
      "number": 4,
      "text": "And one went in, and told his lord, saying, Thus and thus said the maid that is of the land of Israel."
    },
    {
      "number": 5,
      "text": "And the king of Syria said, Go to, go, and I will send a letter unto the king of Israel. And he departed, and took with him ten talents of silver, and six thousand pieces of gold, and ten changes of raiment."
    },
    {
      "number": 6,
      "text": "And he brought the letter to the king of Israel, saying, Now when this letter is come unto thee, behold, I have therewith sent Naaman my servant to thee, that thou mayest recover him of his leprosy."
    },
    {
      "number": 7,
      "text": "And it came to pass, when the king of Israel had read the letter, that he rent his clothes, and said, Am I God, to kill and to make alive, that this man doth send unto me to recover a man of his leprosy? wherefore consider, I pray you, and see how he seeketh a quarrel against me."
    },
    {
      "number": 8,
      "text": "And it was so, when Elisha the man of God had heard that the king of Israel had rent his clothes, that he sent to the king, saying, Wherefore hast thou rent thy clothes? let him come now to me, and he shall know that there is a prophet in Israel."
    },
    {
      "number": 9,
      "text": "So Naaman came with his horses and with his chariot, and stood at the door of the house of Elisha."
    },
    {
      "number": 10,
      "text": "And Elisha sent a messenger unto him, saying, Go and wash in Jordan seven times, and thy flesh shall come again to thee, and thou shalt be clean."
    },
    {
      "number": 11,
      "text": "But Naaman was wroth, and went away, and said, Behold, I thought, He will surely come out to me, and stand, and call on the name of the LORD his God, and strike his hand over the place, and recover the leper."
    },
    {
      "number": 12,
      "text": "Are not Abana and Pharpar, rivers of Damascus, better than all the waters of Israel? may I not wash in them, and be clean? So he turned and went away in a rage."
    },
    {
      "number": 13,
      "text": "And his servants came near, and spake unto him, and said, My father, if the prophet had bid thee do some great thing, wouldest thou not have done it? how much rather then, when he saith to thee, Wash, and be clean?"
    },
    {
      "number": 14,
      "text": "Then went he down, and dipped himself seven times in Jordan, according to the saying of the man of God: and his flesh came again like unto the flesh of a little child, and he was clean."
    }
  ]
};
  const definitions = [
    ['isaiah61', 'Isaiah 61:1–3', 'ot/isa/61', 1, 3],
    ['isaiah61-beauty', 'Isaiah 61:3', 'ot/isa/61', 3, 3],
    ['luke4-reading', 'Luke 4:16–21', 'nt/luke/4', 16, 21],
    ['luke4-fulfilled', 'Luke 4:21', 'nt/luke/4', 21, 21],
    ['luke4-response', 'Luke 4:22–27', 'nt/luke/4', 22, 27],
    ['widow', '1 Kings 17:8–16', 'ot/1-kgs/17', 8, 16],
    ['naaman', '2 Kings 5:1–14', 'ot/2-kgs/5', 1, 14],
    ['luke4-anger', 'Luke 4:28–30', 'nt/luke/4', 28, 30],
    ['luke4-discussion', 'Luke 4:22–30', 'nt/luke/4', 22, 30]
  ];
  const passages = definitions.map(([key, title, path, first, last]) => {
    const range = first === last ? `p${first}` : `p${first}-p${last}`;
    return Object.freeze({key, title, path, range,
      source: `https://www.churchofjesuschrist.org/study/scriptures/${path}?lang=eng&id=${range}#p${first}`,
      verses: chapters[path].filter(verse => verse.number >= first && verse.number <= last)
    });
  });
  function forSource(source) {
    try {
      const url = new URL(source);
      if (!['www.churchofjesuschrist.org', 'churchofjesuschrist.org'].includes(url.hostname)) return null;
      const path = url.pathname.replace('/study/scriptures/', '').replace(/\/$/, '');
      return passages.find(passage => passage.path === path && passage.range === url.searchParams.get('id')) || null;
    } catch {return null;}
  }
  function paginate(verses, wordLimit = 78) {
    const pages = [];
    let page = [], words = 0;
    for (const verse of verses) {
      const length = verse.text.trim().split(/\s+/).length;
      if (page.length && (words + length > wordLimit || page.length === 3)) {
        pages.push(page);page = [];words = 0;
      }
      page.push(verse);words += length;
    }
    if (page.length) pages.push(page);
    return pages;
  }
  globalThis.LessonReadings = Object.freeze({passages, forSource, paginate});
})();
