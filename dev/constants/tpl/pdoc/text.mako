## Define mini-templates for each portion of the doco.

<%def name="h(hs, s, link=None)" buffered="True">
    <%
        if link is None:
            link = s
        header = f'<a href="#{link}" id="{link}">{s}</a>'
        match hs:
            case 4:
                hs = 3
                header = f'<b><i>{header}</i></b>'
            case 5:
                hs = 3
            case 6:
                hs = 3
                header = f'<i>{header}</i>'
            case _:
                header = f'<b>{header}</b>'
        header = f'<h{hs}>{header}</h{hs}>'
    %>
${header}

</%def>
<%def name="ds(s, hs, link=None)" buffered="True">
    <%
        if link is None:
            link = ""
        for i in ["Args", "Raises", "Returns", "Yields"]:
            s = s.replace(f'{i}:', h(hs, i + ':', link + i.lower()))
    %>
${s}
</%def>
<%def name="function(func, hs, cls=None)" buffered="True">
    <%
        if cls is None:
            link = f'func-{func.name}'
        else:
            link = f'class-{cls}-func-{func.name}'
        header = h(hs, func.name, link)
        returns = show_type_annotations and func.return_annotation() or ''
        if returns:
            returns = ' \N{non-breaking hyphen}> ' + returns
    %>


${header}
```python
(${", ".join(func.params(annotate=show_type_annotations))})${returns}
```
${ds(func.docstring, hs + 2, link + '-')}</%def>
<%def name="variable(var)" buffered="True">
    <%
        annot = show_type_annotations and var.type_annotation() or ''
        if annot:
            annot = ': ' + annot
    %>
`${var.name}${annot}`

${var.docstring}
</%def>

<%def name="class_(cls)" buffered="True">
${h(4, cls.name, f'class-{cls.name}')}```python
(${", ".join(cls.params(annotate=show_type_annotations))})
```
<%
    class_vars = cls.class_variables(show_inherited_members, sort=sort_identifiers)
    static_methods = cls.functions(show_inherited_members, sort=sort_identifiers)
    inst_vars = cls.instance_variables(show_inherited_members, sort=sort_identifiers)
    methods = cls.methods(show_inherited_members, sort=sort_identifiers)
    mro = cls.mro()
    subclasses = cls.subclasses()
    link = f'class-{cls.name}-'
%>
${ds(cls.docstring, 5, link)}
% if mro:
${h(5, 'Ancestors (in MRO)', link + 'mro')}
% for c in mro:
* ${c.refname}
% endfor

% endif
% if subclasses:
${h(5, 'Descendants', link + 'sub')}
% for c in subclasses:
* ${c.refname}
% endfor

% endif
% if class_vars:
${h(5, 'Class variables', link + 'cvar')}
% for v in class_vars:
${variable(v)}

% endfor
% endif
% if static_methods:
${h(5, 'Static methods', link + 'sfunc')}
% for f in static_methods:
${function(f, 6, cls.name)}

% endfor
% endif
% if inst_vars:
${h(5, 'Instance variables', link + 'var')}
% for v in inst_vars:
${variable(v)}

% endfor
% endif
% if methods:
${h(5, 'Methods', link + 'func')}
% for m in methods:
${function(m, 6, cls.name)}

% endfor
% endif
</%def>

## Start the output logic for an entire module.

<%
variables = module.variables(sort=sort_identifiers)
classes = module.classes(sort=sort_identifiers)
functions = module.functions(sort=sort_identifiers)
submodules = module.submodules()

header = []
m, *ls = module.name.split(".")
for idx, i in enumerate(ls[::-1]):
    header.append(f'[{i}]({"../" * idx}{i}.md)')

header = '.'.join([f'[{m}](' + '../' * (len(ls) - 1) + 'index.md)'] + header[::-1])
%>

% if module.docstring:
${h(2, 'Module Reference', 'mr')}
${ds(module.docstring, 3)}
% endif

## % if submodules:
## ${h(3, 'Sub-modules', 'sub')}
## % for m in submodules:
## * ${m.name}
## % endfor
## % endif

% if variables:
${h(3, 'Variables', 'var')}
% for v in variables:
${variable(v)}

% endfor
% endif

% if functions:
${h(3, 'Functions', 'func')}
% for f in functions:
${function(f, 4)}

% endfor
% endif

% if classes:
${h(3, 'Classes', 'class')}
% for c in classes:
${class_(c)}

% endfor
% endif
