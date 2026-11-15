// Run with a Node runtime that provides @oai/artifact-tool.
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import * as art from '@oai/artifact-tool';
import { buildSlides, slideSize } from './slides.mjs';
const dir=path.dirname(fileURLToPath(import.meta.url));
const out=path.resolve(dir,'..');
const build=path.resolve(out,'../.mathathon-build');
await fs.mkdir(build,{recursive:true});
const p=art.Presentation.create({slideSize});
buildSlides(p);
await (await art.PresentationFile.exportPptx(p)).save(path.join(build,'slides-draft.pptx'));
console.log(JSON.stringify({slides:p.slides.items.length,pptx:path.join(build,'slides-draft.pptx')}));
// Convert the final PPTX to PDF with PowerPoint or LibreOffice; see HANDOFF.md.
