"""Lesson-specific workflow. Read this file before the execution adapter."""
from __future__ import annotations
import asyncio
import json
from pathlib import Path
from runtime import atomic_json, contained_path, in_process_tool

async def run(agent, data):
    rows = data['sales']
    known = [row['revenue'] for row in rows if row['revenue'] is not None]
    if any(type(value) not in (int, float) or value < 0 for value in known):
        raise ValueError('Known revenue must be a nonnegative number')
    evidence = {'snapshot': data['snapshot'], 'currency': data['currency'],
                'known_total': sum(known), 'missing': len(rows) - len(known)}
    explanation = await agent.ask('stream_summary', 'Explain this incomplete sales snapshot. Do not replace missing revenue with zero.',
        evidence, f"Known revenue is {sum(known)} {data['currency']}; {evidence['missing']} value is missing.", streaming=True)
    followup = await agent.conversation(
        [f'Here is the snapshot: {json.dumps(evidence)}. Summarize its limitation.', 'Which limitation matters most?'],
        ['The total excludes missing revenue.', 'The known total is incomplete, not the final total.'])
    return {'evidence': evidence, 'explanation': explanation, 'followup': followup[-1]}
