{% macro clean_salary(col) %} 

case
     when {{col}} is null then null     
     when try_cast(regexp_replace({{col}}, '[^0-9.]', '') as double) is null then null 
     else cast(regexp_replace({{col}}, '[^0-9.]', '') as double) 
end

{% endmacro %}

