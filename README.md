# The Vivisection Lab

**Live site → [an0nya.github.io/vivisection-lab](https://an0nya.github.io/vivisection-lab/)**

A lab notebook: small open-weight language models taken apart layer by layer on a
16 GB Mac Mini — no GPUs, no cloud. Duplicate a layer so the signal passes through
twice, delete one and stitch the network back together, inject a direction into the
residual stream, then score what happened *honestly*. Most of these surgeries make
the patient worse; a few make it better; the most seductive results turn out to be
artifacts of how you measured.

The method extends David Ng's [RYS ("Repeat Your Self")](https://huggingface.co/blog/dnhkng/blog-1)
layer-duplication work onto architectures it was never designed for, paired with a
strict-grading discipline that keeps catching the pretty results lying.

## The specimens

| Page | Specimen | What it covers |
|------|----------|----------------|
| [**Gemma 4**](https://an0nya.github.io/vivisection-lab/gemma.html) | dense 4B + 26B MoE | A 42-layer model duplicated/pruned one block at a time; a mixture-of-experts that refuses the same scalpel; the 31B sibling, parked. |
| [**Granite**](https://an0nya.github.io/vivisection-lab/granite.html) | dense 3B | Direction vs magnitude, a depth-vulnerability curve, a full dup/prune map of all 40 layers, and a dose-response that finds the lethal dose. |
| [**HRM**](https://an0nya.github.io/vivisection-lab/hrm.html) *(draft)* | recurrent | A beautiful overnight "more-loops-helps" finding — and the verification pass that demolished it. |
| [**Internal geometry**](https://an0nya.github.io/vivisection-lab/geometry.html) | cross-model | Per-layer cross-language cosine/delta scans across nine models — where meaning goes language-agnostic in the middle of the stack. |

## Method notes

Everything ran locally on a `$599` Mac Mini M4. The original technique was for
somebody with H100s; this is for somebody with a kitchen. Two of the most exciting
findings here were wrong, and both are kept on the page with the autopsy — a lab
notebook that only records confirmed results isn't a notebook, it's a brochure.

Models are property of their respective authors (Google · IBM Granite · Sapient /
Aryagm) under their respective licenses. Probing, scoring, and plots are the author's.
