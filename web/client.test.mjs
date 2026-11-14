import test from 'node:test';
import assert from 'node:assert/strict';
import { creerClient } from './client.js';

const cle = 'cle-fictive-pour-tests-client';
const url = 'http://127.0.0.1:8000';
const succes = data => async () => ({ok:true,status:200,json:async()=>data});

test('santé : route publique /v1/health', async () => {
  let appel;
  const c = creerClient(url, '', async (...args) => { appel=args; return {ok:true,json:async()=>({status:'OK'})}; });
  assert.equal((await c.sante()).data.status,'OK'); assert.equal(appel[0],url+'/v1/health');
  assert.equal(appel[1].headers['X-API-Key'],undefined);
});
test('prédiction : route, JSON et clé client', async () => {
  let appel;
  const c=creerClient(url,cle,async (...args)=>{appel=args;return {ok:true,json:async()=>({label:'POSITIVE',score:.777})};});
  const r=await c.predire('Très satisfait'); assert.equal(r.ok,true);
  assert.equal(appel[0],url+'/v1/predict'); assert.equal(appel[1].headers['X-API-Key'],cle);
  assert.deepEqual(JSON.parse(appel[1].body),{text:'Très satisfait'});
});
test('verdict négatif lisible',async()=>assert.equal((await creerClient(url,cle,succes({label:'NEGATIVE',score:.75})).predire('Cassé')).message,'Avis négatif'));
test('abstention : transmettre au contrôle humain',async()=>assert.match((await creerClient(url,cle,succes({label:'INDETERMINE',score:.52})).predire('Inconnu')).message,/humain/));
for(const [status,code,motif] of [[401,'NON_AUTHENTIFIE',/clé/i],[403,'ACCES_REFUSE',/rôle/],[422,'ENTREE_INVALIDE',/Texte refusé/],[500,'ERREUR_INTERNE',/Erreur interne/],[503,'MODELE_INDISPONIBLE',/indisponible/]]) {
  test(`erreur stable ${status} ${code}`,async()=>{
    const c=creerClient(url,cle,async()=>({ok:false,status,json:async()=>({erreur:{code,message:'message variable',champs:[]}})}));
    const r=await c.predire('Texte');assert.equal(r.ok,false);assert.equal(r.code,code);assert.match(r.message,motif);
  });
}
test('réponse mal formée et adresse invalide',async()=>{
  assert.equal((await creerClient(url,cle,succes({label:'AUTRE',score:5})).predire('Texte')).ok,false);
  const c=creerClient(url,cle,async()=>({ok:true,json:async()=>{throw Error('json');}}));
  assert.match((await c.predire('Texte')).message,/illisible/);
  assert.throws(()=>creerClient('file:///etc/passwd'),/Adresse API invalide/);
});
test('API injoignable : message explicite',async()=>{
  const c=creerClient(url,cle,async()=>{throw Error('network');});assert.equal((await c.predire('Texte')).code,'API_INJOIGNABLE');
});
test('clé absente : aucun envoi du texte',async()=>{
  let appels=0;const c=creerClient(url,'',async()=>{appels++;});
  assert.equal((await c.predire('Texte privé')).code,'NON_AUTHENTIFIE');assert.equal(appels,0);
});
