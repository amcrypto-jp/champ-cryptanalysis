-- Keep section headings with the text that follows in the PDF.
function Header(h)
  if FORMAT:match('latex') then
    return {pandoc.RawBlock('latex', '\\Needspace{5\\baselineskip}'), h}
  end
end

-- Explicit widths prevent long prose cells from squeezing mathematical columns.
function Table(t)
  local n = #t.colspecs
  if n == 4 then
    t.colspecs = {{pandoc.AlignLeft, .30}, {pandoc.AlignCenter, .17},
                 {pandoc.AlignCenter, .17}, {pandoc.AlignLeft, .36}}
  elseif n == 3 then
    local text = pandoc.utils.stringify(t.head)
    if text:find('Field bits', 1, true) then
      t.colspecs = {{pandoc.AlignLeft, .17}, {pandoc.AlignRight, .25},
                   {pandoc.AlignLeft, .58}}
    else
      t.colspecs = {{pandoc.AlignLeft, .40}, {pandoc.AlignRight, .10},
                   {pandoc.AlignLeft, .50}}
    end
  end
  if FORMAT:match('latex') then
    local lines = n == 4 and 16 or 9
    return {pandoc.RawBlock('latex', '\\Needspace{' .. lines .. '\\baselineskip}'), t}
  end
  return t
end

-- Allow DOI text to wrap using URL break rules rather than extending the margin.
function Link(link)
  local label = pandoc.utils.stringify(link.content)
  if FORMAT:match('latex') and label:match('^10%.') then
    return pandoc.RawInline('latex', '\\href{' .. link.target .. '}{\\nolinkurl{' .. label .. '}}')
  end
end

-- Keep the short paragraph introducing a display together with that display.
function Pandoc(doc)
  if not FORMAT:match('latex') then return doc end
  local blocks = pandoc.List()
  for i, block in ipairs(doc.blocks) do
    local following = doc.blocks[i + 1]
    local after = doc.blocks[i + 2]
    if block.t == 'Para' and pandoc.utils.stringify(block):match('^AI%-use disclosure%.') then
      blocks:insert(pandoc.RawBlock('latex', '\\Needspace{8\\baselineskip}'))
    end
    if block.t == 'Header' and following and following.t == 'Para'
        and after and after.t == 'Para' and #after.content == 1
        and after.content[1].t == 'Math'
        and after.content[1].mathtype == 'DisplayMath' then
      local n = math.min(12, math.ceil(#pandoc.utils.stringify(following) / 85) + 5) + 4
      blocks:insert(pandoc.RawBlock('latex', '\\Needspace{' .. n .. '\\baselineskip}'))
    end
    if block.t == 'Para' and following and following.t == 'Para'
        and #following.content == 1 and following.content[1].t == 'Math'
        and following.content[1].mathtype == 'DisplayMath' then
      local n = math.min(12, math.ceil(#pandoc.utils.stringify(block) / 85) + 5)
      blocks:insert(pandoc.RawBlock('latex', '\\Needspace{' .. n .. '\\baselineskip}'))
    end
    blocks:insert(block)
  end
  doc.blocks = blocks
  return doc
end
