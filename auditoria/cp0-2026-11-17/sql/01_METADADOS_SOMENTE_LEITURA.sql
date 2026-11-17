-- PREPARADO / NAO EXECUTADO.
-- Confirmar no conector/console project ref gixxspfvcgxumyxnyumi ANTES de executar.
-- current_database() normalmente e postgres e NAO confirma o project ref.
-- Apenas metadados: nao le linhas de artistas, credenciais ou conteudo de arquivos.
BEGIN TRANSACTION READ ONLY;
SET LOCAL statement_timeout = '15s';
SET LOCAL lock_timeout = '2s';

SELECT current_database() AS database_name, current_user AS executor,
       current_setting('transaction_read_only') AS read_only;

SELECT n.nspname AS schema_name, c.relname AS relation_name, c.relkind,
       c.relrowsecurity, c.relforcerowsecurity
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE (n.nspname='public' AND c.relname LIKE 'stagekit_%')
   OR n.nspname='stagekit_private'
   OR (n.nspname='storage' AND c.relname IN ('objects','buckets'))
ORDER BY 1,2;

SELECT table_schema,table_name,column_name,data_type,udt_name,is_nullable
FROM information_schema.columns
WHERE (table_schema='public' AND table_name LIKE 'stagekit_%')
   OR (table_schema='auth' AND table_name='users')
   OR (table_schema='storage' AND table_name IN ('objects','buckets'))
ORDER BY table_schema,table_name,ordinal_position;

SELECT n.nspname,c.relname,con.conname,con.contype,
       pg_get_constraintdef(con.oid) AS constraint_definition
FROM pg_constraint con JOIN pg_class c ON c.oid=con.conrelid
JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname='public' AND c.relname LIKE 'stagekit_%'
ORDER BY 1,2,3;

SELECT schemaname,tablename,indexname,indexdef
FROM pg_indexes WHERE schemaname='public' AND tablename LIKE 'stagekit_%'
ORDER BY 1,2,3;

SELECT schemaname,tablename,policyname,permissive,roles,cmd,qual,with_check
FROM pg_policies
WHERE (schemaname='public' AND tablename LIKE 'stagekit_%')
   OR schemaname='stagekit_private'
   OR (schemaname='storage' AND tablename IN ('objects','buckets'))
ORDER BY 1,2,3;

SELECT table_schema,table_name,grantee,privilege_type,is_grantable
FROM information_schema.table_privileges
WHERE (table_schema='public' AND table_name LIKE 'stagekit_%')
   OR table_schema='stagekit_private'
   OR (table_schema='storage' AND table_name IN ('objects','buckets'))
ORDER BY 1,2,3,4;

SELECT table_schema,table_name,column_name,grantee,privilege_type
FROM information_schema.column_privileges
WHERE table_schema='public' AND table_name LIKE 'stagekit_%'
ORDER BY 1,2,3,4,5;

SELECT object_schema,object_name,object_type,grantee,privilege_type
FROM information_schema.usage_privileges
WHERE object_schema IN ('public','stagekit_private')
ORDER BY 1,2,4,5;

SELECT n.nspname,c.relname,t.tgname,t.tgenabled,
       pg_get_triggerdef(t.oid) AS trigger_definition
FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid
JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE NOT t.tgisinternal
  AND ((n.nspname='public' AND c.relname LIKE 'stagekit_%')
    OR n.nspname='stagekit_private')
ORDER BY 1,2,3;

-- Nao exporta corpos de funcao: fingerprint permite detectar mudancas sem expor segredos.
SELECT n.nspname,p.proname,pg_get_function_identity_arguments(p.oid) AS arguments,
       pg_get_userbyid(p.proowner) AS owner,p.prosecdef AS security_definer,
       EXISTS(SELECT 1 FROM unnest(p.proconfig) cfg WHERE cfg LIKE 'search_path=%') AS search_path_is_configured,
       has_function_privilege('anon',p.oid,'EXECUTE') AS anon_execute,
       has_function_privilege('authenticated',p.oid,'EXECUTE') AS authenticated_execute,
       md5(pg_get_functiondef(p.oid)) AS definition_fingerprint
FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
WHERE p.prokind='f' AND (n.nspname='stagekit_private'
   OR (n.nspname='public' AND p.proname LIKE 'stagekit_%'))
ORDER BY 1,2,3;

SELECT id,name,public,file_size_limit,allowed_mime_types
FROM storage.buckets WHERE id='stagekit-media' OR name='stagekit-media';

ROLLBACK;
-- Auth, backups/PITR, planos, SMTP, Edge Functions e Vercel requerem leitura de gestao.
-- Queries de vinculos agregados dependem de confirmar schema/colunas antes de prepara-las.
