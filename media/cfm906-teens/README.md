# September 6 Sunday School, ages 16-17

Public entry: `/cfm906-teens.html`. A separate version of the same September 6 lesson, with quiet reflection, situations to discuss, and a question to explore at home. The existing adult and younger youth pages are unchanged. The site does not collect student responses or use accounts.

## Teaching choices and sources

The [official September 6 instructions](https://www.churchofjesuschrist.org/study/manual/changes-to-the-sunday-class-meeting-schedule-instruction-2026/youth-and-adult-sunday-instruction-materials?lang=eng) assign both videos and discussion after each. This page includes both complete videos. The same English captions and video files are reused from the original lesson.

The adaptations follow [Invite Diligent Learning](https://www.churchofjesuschrist.org/study/manual/teaching-in-the-saviors-way-2022/07-part-2/11-invite-diligent-learning?lang=eng): give learners time to ponder, invite their questions, let them learn from each other, and invite action. The scenarios and pause questions are teaching suggestions for this class, not additional Church instructions.

| Video | Displayed stop | Trigger | Activity |
| --- | --- | --- | --- |
| The Sabbath and Sacrament Meeting | 3:08 | 188.0 seconds | 30 seconds to note an idea about Christ's forgiveness |
| The Sabbath and Sacrament Meeting | 7:21 | 440.5 seconds | 30 seconds to consider a choice during sacrament meeting |
| Sunday School | 2:33 | 153.2 seconds | 45 seconds for partners to share a question or a starting point |

Stops fall in gaps between sentences in the supplied captions. Labels round to the nearest second. They fire once in normal playback; seeking past a stop skips it. Teachers can disable all guided stops or preview prompts without consuming them. Activity timers never resume video playback.

The suggested plan totals 22 minutes, including 75 seconds of discussion after each video. Three minutes remain for arrivals and transitions. All six optional activities are available through Extras & activities: Psalms moment, praise wall, phrase reveal, New Testament matching, verse puzzle, and phrase reflection. They draw on [this week's Come, Follow Me lesson](https://www.churchofjesuschrist.org/study/manual/come-follow-me-for-home-and-church-old-testament-2026/36?lang=eng) and use KJV scripture text.

## Media and handout

`Reverential Return` remains the sharing image. It and `Light and Trees` are existing lesson images used with the permission confirmed by the teacher. Sources and credits are recorded in `../cfm906/images/README.md` and displayed in the lesson. The OTW logo is not clickable; there are no navigation links to the main site or other lesson versions.

The handout has two identical half-sheet cards on one US Letter page. Print one card per student, single-sided, at actual size. Students keep their own notes; no collection is part of the lesson. Class size is left open for this version.

- Rebuild handout: `python3 tools/build_cfm906_teens_handout.py` (ReportLab required).
- Interaction checks: `node tools/test_cfm906_teens.mjs` (Python 3 also required). These use a simulated DOM, not browser rendering.
- Local reference audit: `python3 tools/audit_public_site.py --strict`.

The PDF is rendered and visually reviewed separately. Test classroom sound before teaching.

Shared activity behavior and scripture passages live in `../cfm906/extras.js`; shared layouts are in `../cfm906/extras.css`. Each page loads them before its own controller. Existing `#psalm` links still open this edition’s original activity.

Run `node tools/test_cfm906_extras.mjs` for all six activities across the three lessons, and `node tools/test_cfm906_start.mjs` for return-to-start behavior. Both use a simulated DOM.
