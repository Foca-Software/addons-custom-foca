select p.id, name, product_tmpl_id
from product_product p
inner join product_template on p.product_tmpl_id = product_template.id
order by name;


select * from stock_picking
order by id desc;

select id,name,code,active from account_journal;


select id,active,name from l10n_latam_document_type;