---
name: cola-voice-delivery
description: Generate and deliver long-form Chinese narration through ListenHub using the Xiaoman and Cola female voices. Use when the user asks to read a full text, split a long script into audio parts, provide both segmented and merged MP3 files, compare or preserve Xiaoman/晓曼 and Cola voices, or asks for the same audio in both voices. This skill is Cola/ListenHub-specific and requires the ListenHub TTS capability plus local file download and audio concatenation.
metadata:
  category: audio
  language: zh
---

# Cola Voice Delivery

Generate long Chinese scripts in two named ListenHub voices and deliver every segment plus a complete merged MP3. The workflow exists to prevent long-input failures and accidental overwrites between voice variants.

## Simple Invocation

Treat the skill call plus an attached text file as the complete user input. Do not ask the user to split, paste, upload, rename, download, or merge anything. The default output is both voices:

- `晓曼`: all ordered MP3 chunks plus one merged MP3
- `Cola`: all ordered MP3 chunks plus one merged MP3

The number of chunks is dynamic: choose it from the source length and reliable TTS input size, not from a fixed count. A short text may produce one chunk; a long podcast script may produce many. A successful run is not complete until all files are locally present and every file is delivered with a `MEDIA:` line. If the user explicitly requests only one voice, deliver that voice's complete set; otherwise generate both.

## Voice Registry

Use these exact ListenHub speaker IDs:

- Xiaoman / 晓曼: `chat-girl-105-cn`
- Cola: `chatb812x-500306f5`

Do not substitute one voice for the other. In the final response, state the exact voice used for every file group.

## Accepted Input

Accept either raw text or an attached text/document file. If the input is a podcast audio file or podcast URL, transcribe it first with an ASR/transcription capability, then use the resulting transcript as the narration source. Keep the transcript's order and separate speakers or sections when they are meaningful.

## Generation Strategy

Use a two-pass, section-preserving pipeline rather than sending a long attachment or private file URL to ListenHub:

1. Normalize the source into speakable text while retaining the original narrative order and meaningful section titles.
2. Split at chapter or section boundaries so each TTS request stays within a reliable input size and a failed request can be retried without regenerating the whole book.
3. Generate the same ordered chunk set once with Xiaoman and once with Cola. Keep the voice runs independent so a failure or retry in one voice cannot replace the other.
4. Poll each ListenHub episode to success, then download its returned `audioUrl`. Use the generated audio URL, not the service's outline or summary.
5. Store chunks under voice-specific directories and merge only after every expected chunk is present. Verify duration and size for both merged outputs.
6. Deliver every chunk and both merged files. This makes individual chapter replacement possible and keeps the complete audiobook convenient to play.

Passing raw chunk text directly is intentional: ListenHub may reject local paths and private uploaded text URLs as invalid sources. If the ListenHub endpoint specifically requires a URL or HTML source, create a temporary HTML document containing escaped source text inside an article element, upload it only with the user's authorization, and pass the resulting fetchable URL. Treat HTML as a fallback transport, not as a replacement for direct chunk generation; if the HTML URL is rejected, return to direct chunk text. Separate names and directories are equally intentional: a shared output name can overwrite a previously valid voice version.

## Workflow

1. Read or transcribe the complete input before generating audio. Preserve the source order and wording. Remove only markup that should not be spoken, such as Markdown heading syntax, unless the user asks for literal document reading. Keep meaningful section titles and narration cues when they are part of the script.
2. Estimate the reliable input size and split dynamically. Prefer section boundaries (`##`, chapter titles, or natural paragraph breaks), then split oversized sections at paragraph boundaries. Use as many chunks as needed; never force a fixed number such as 11. Name chunks with zero-padded indexes: `00`, `01`, `02`, and so on.
3. For each requested voice, call ListenHub `create_tts` with:
   - `language: zh`
   - `tts_type: text`
   - `tts_mode: direct`
   - the selected speaker ID
   - the raw text of exactly one chunk
4. Poll each returned episode with `check_status` until `processStatus` is `success`. Record the returned `audioUrl` in chunk order. Do not use the episode outline as the audio source; it may be a summary rather than the supplied script.
5. Download every successful audio URL locally. Use separate directories for each voice, for example:
   - `xiaoman-listenhub-parts/00.mp3`
   - `cola-listenhub-parts/00.mp3`
6. Merge each voice's chunks with the bundled `scripts/merge_mp3.sh` or an equivalent FFmpeg concat workflow. Use separate, explicit output names:
   - `全文朗读-晓曼-ListenHub合并版.mp3`
   - `全文朗读-Cola-ListenHub合并版.mp3`
   Never write both variants to a shared filename.
7. Verify each merged file with an audio probe. Report duration and file size, and make sure all expected chunk files exist before delivery.
8. Deliver one `MEDIA: /absolute/path` line for every file: both merged files and all segmented files for both voices. Do not deliver only a directory or only the merged versions.

## Input and Failure Handling

- If a local attachment cannot be passed directly to ListenHub, read it locally and pass chunk text directly to `create_tts`. Do not pass a local path as the narration content: ListenHub will read the path literally or reject it.
- If a private uploaded text URL is rejected as `Invalid input at source`, stop retrying that URL and use direct chunk text instead.
- If a generation succeeds but downloading its `audioUrl` times out, retry against the returned ListenHub asset host and preserve the episode ID and URL mapping.
- If a voice generation fails, do not silently substitute the other voice. Report the failed voice and keep any successfully generated voice files.
- Preserve existing files by choosing a new, voice-specific filename. Overwriting a previous voice's merged file loses a valid deliverable.
- For a long script, generation may be paid and may take several minutes. Track the work as a multi-step task and mark it completed only after both requested voice groups, their chunks, and their merged files have been verified.

## Final Acceptance Check

Before answering, verify the complete chain, not just that one TTS request succeeded:

1. The raw text or podcast transcript was read completely and its section order was preserved.
2. A dynamic chunk count was chosen from the input length; no fixed segment count was assumed.
3. The same dynamically chosen chunk indexes exist for both requested voices.
4. Every chunk has a downloaded, non-empty MP3 file.
5. Each voice has a separate merged MP3, with no shared filename or overwrite.
6. FFprobe or an equivalent audio probe reports duration and size for both merged files.
7. The final response identifies the two exact speaker IDs and contains one `MEDIA:` line for every chunk and every merged file.

If any check fails, keep working or report the specific failed voice/chunk; do not claim full delivery.

## Delivery Checklist

- [ ] Correct speaker ID used for every generation
- [ ] All source sections covered in order
- [ ] Every chunk downloaded for each requested voice
- [ ] Merged files have distinct voice-specific names
- [ ] Duration and file size checked
- [ ] All chunk files and both merged files delivered with `MEDIA:` lines
