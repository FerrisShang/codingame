//https://www.codingame.com/multiplayer/bot-programming/tic-tac-toe
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <sys/time.h>
#include <time.h>

#define NDEBUG
#include <assert.h>

#define DEFAULT_TIME_PER_MOVE (CLOCKS_PER_SEC/1000*90)

int TIME_START, TEST_VALUE, TEST_FLAG;

enum ID{ EMPTY = 0, ID0 = 1, ID1 = 2, };
enum win_map_state{ UNKNOWN = 0, ID0_WIN = 1, ID1_WIN = 2, DRAW_FULL = 3 };
enum score{ SC_INVALID = -(1<<24), SC_ZERO = 0, SC_WIN = 1};
char win_map[1 << 18];
char win_map_all[1 << 18];
int field_pos_map[9][9];
int field_off_map[9][9];
int field_off_map_set[9][9][4];
int field_off_map_clear[9][9];

#define MSG(fmt, ...)                 fprintf(stderr, "DEBUG: " fmt, __VA_ARGS__)
#define OP_ID(id)                     (3-(id))
#define FIELD_ALL                     9
#define SET(field, x, y, id)          field[field_pos_map[y][x]] |= field_off_map_set[y][x][id]
#define CLEAR(field, x, y)            field[field_pos_map[y][x]] &= field_off_map_clear[y][x]
#define GET_POS(x, y)                 field_pos_map[y][x]
#define IS_VALID(field, x, y)         ((field[field_pos_map[y][x]] | field_off_map_clear[y][x])==field_off_map_clear[y][x])
#define GET_POS_ID(N, x, y)           ((N >> 2*(y*3+x)) & 0x03)
#define GET_STATE(field, pos)         win_map[field[pos]]
#define GET_STATE_XY(field, x, y)     win_map[field[field_pos_map[y][x]]]
#define GET_STATE_ALL(field)     win_map_all[field[FIELD_ALL]]
#define UPDATE_FIELD_ADD(field, x, y) do{int pos=GET_POS(x, y); field[FIELD_ALL] |= GET_STATE(field, pos) << 2*pos;}while(0)
#define UPDATE_FIELD_ALL(field)       do{int _;field[FIELD_ALL]=0;for(_=0;_<9;_++){field[FIELD_ALL] |= GET_STATE(_) << 2*_;}}while(0)

struct node{
	int field[10];
	int id;
	int valid_move_cnt;
	unsigned char valid_moves[84];
	int moved_cnt;
	unsigned char moveds[84];
	struct node *p_nmn[9][9]; // next move node

	int win_state;
	int score;
	int sim_score;
	float mcts_score;

	int last_move;
	float child_max_score;
	struct node * child_best;
	int simulations;
	int result;
};

struct mcts{
	struct node *root;
	int simulate_cnt;
	int x, y;
}mcts;

void init_maps(void){
	int n,i,j,id;
	TIME_START = time(NULL);
	MSG("SEED:%d\n", TIME_START & 0xFFFF);
	srand(TIME_START & 0x0);
	for(j=0;j<9;j++){
		for(i=0;i<9;i++){
			field_pos_map[j][i] = (j/3)*3 + i/3;
			field_off_map[j][i] =((j%3)*3 + i%3) * 2;
			field_off_map_clear[j][i] = ~(0x03 << ((j%3)*3 + (i%3)) * 2);
			for(id=1;id<=2;id++) field_off_map_set[j][i][id] = id << ((j%3)*3 + (i%3)) * 2;
		}
	}
	// init win map
	for(n=0;n<(1 << 18);n++){
		#define _GPI(N, x, y) GET_POS_ID(N, x, y)
		if((_GPI(n, 0, 0) == ID0 || _GPI(n, 0, 0) == ID1) && ((_GPI(n, 0, 0) == _GPI(n, 1, 0) && _GPI(n, 1, 0) == _GPI(n, 2, 0)) || (_GPI(n, 0, 0) == _GPI(n, 0, 1) && _GPI(n, 0, 1) == _GPI(n, 0, 2)))){win_map[n] = _GPI(n, 0, 0); win_map_all[n] = _GPI(n, 0, 0);}
		else if((_GPI(n, 1, 1) == ID0 || _GPI(n, 1, 1) == ID1) && (
				(_GPI(n, 0, 1) == _GPI(n, 1, 1) && _GPI(n, 1, 1) == _GPI(n, 2, 1)) || (_GPI(n, 1, 0) == _GPI(n, 1, 1) && _GPI(n, 1, 1) == _GPI(n, 1, 2)) ||
				(_GPI(n, 0, 0) == _GPI(n, 1, 1) && _GPI(n, 1, 1) == _GPI(n, 2, 2)) || (_GPI(n, 0, 2) == _GPI(n, 1, 1) && _GPI(n, 1, 1) == _GPI(n, 2, 0)))){win_map[n] = _GPI(n, 1, 1);win_map_all[n] = _GPI(n, 1, 1);}
		else if((_GPI(n, 2, 2) == ID0 || _GPI(n, 2, 2) == ID1) && ((_GPI(n, 0, 2) == _GPI(n, 1, 2) && _GPI(n, 1, 2) == _GPI(n, 2, 2)) || (_GPI(n, 2, 0) == _GPI(n, 2, 1) && _GPI(n, 2, 1) == _GPI(n, 2, 2)))){win_map[n] = _GPI(n, 2, 2); win_map_all[n] = _GPI(n, 2, 2);}
		else if((_GPI(n, 0, 0) != UNKNOWN) && (_GPI(n, 0, 1) != UNKNOWN) && (_GPI(n, 0, 2) != UNKNOWN) &&
			 (_GPI(n, 1, 0) != UNKNOWN) && (_GPI(n, 1, 1) != UNKNOWN) && (_GPI(n, 1, 2) != UNKNOWN) &&
			 (_GPI(n, 2, 0) != UNKNOWN) && (_GPI(n, 2, 1) != UNKNOWN) && (_GPI(n, 2, 2) != UNKNOWN)){
			int id0 = 0, id1 = 0;
			for(i=0;i<3;i++) for(j=0;j<3;j++){
				if(_GPI(n, j, i) == ID0)id0++;else if(_GPI(n, j, i) == ID1)id1++;
			}
			if(id0 > id1) win_map_all[n] = ID0_WIN; else if(id0 < id1) win_map_all[n] = ID1_WIN; else win_map_all[n] = DRAW_FULL;
			win_map[n] = DRAW_FULL;
		}
		else{win_map[n] = UNKNOWN; win_map_all[n] = UNKNOWN;}
	}
}

void mctsCreate(int id);
int get_res(void);
struct node* mctsMoveChildNode(unsigned char point);

void dumpNode(struct node *n)
{
	int i;
	MSG("id:%d valid_move_cnt:%d moved_cnt:%d\n", n->id, n->valid_move_cnt, n->moved_cnt);
	MSG("score:%d mcts_score:%f last_move:%X\n", n->score, n->mcts_score, n->last_move);
	MSG("child_max_score:%f simulations:%d ADDR:%04X\n", n->child_max_score, n->simulations, ((uintptr_t)n)&0xFFFF);
	for(i=0;i<n->valid_move_cnt;i++) fprintf(stderr, "%02X ", n->valid_moves[i]); fprintf(stderr, "\n");
	//for(i=0;i<n->moved_cnt;i++){ fprintf(stderr, "%d ", n->p_nmn[n->moveds[i]>>4][n->moveds[i]&0xF]->simulations); }
	//fprintf(stderr, "\n");
	for(i=0;i<10;i++) MSG("%08X\n", n->field[i]);

}
int dumpCnt(struct node *n)
{
	int i, cnt = n->moved_cnt;
	for(i=0;i<n->moved_cnt;i++){
		unsigned char point = n->moveds[i];
		cnt += dumpCnt(n->p_nmn[point>>4][point&0xF]);
	}
	return cnt;
}
struct node* createNode(int id)
{
	struct node *n = (struct node*)calloc(1, sizeof(struct node));
	n->id = id;
	return n;
}
struct node* growNode(struct node* node, unsigned char point)
{
	struct node *n = (struct node*)calloc(1, sizeof(struct node));
	assert(n != NULL);
	unsigned char y = point >> 4, x = point & 0x0F;
	int valid_move_cnt = 0;
	unsigned char *valid_moves = n->valid_moves;
	int *field = n->field;
	memcpy(n, node, sizeof(int)*10); // only copy 'field'
	// update parameters
	n->id = OP_ID(node->id);
	n->last_move = point;
	n->score = 0;
	n->simulations += 1;
	n->child_max_score = -1;
	node->p_nmn[y][x] = n;
	// update field
	SET(field, x, y, n->id);
	UPDATE_FIELD_ADD(field, x, y);
	//calculate score
	if((n->win_state = GET_STATE_ALL(field)) != UNKNOWN) {
		if(n->id == n->win_state) n->sim_score = SC_WIN;
		else if(OP_ID(n->id) == n->win_state) n->sim_score = -SC_WIN;
		else n->sim_score = SC_ZERO;
		return n;
	}
	//update valid_moves
	if(GET_STATE(field, (y%3)*3+(x%3)) == UNKNOWN){ int bx = (x%3)*3, by = (y%3)*3;
		for(y=by;y<by+3;y++){ for(x=bx;x<bx+3;x++){/**/if(IS_VALID(field, x, y)){ valid_moves[valid_move_cnt++] = (y<<4)|x; }/**/}}
	}else{
		int k;for(k=0;k<9;k++){ if(GET_STATE(field, k)==UNKNOWN){ int bx = (k%3)*3, by = k - (k%3);
			for(y=by;y<by+3;y++){ for(x=bx;x<bx+3;x++){/**/if(IS_VALID(field, x, y)){ valid_moves[valid_move_cnt++] = (y<<4)|x; }/**/}}
		}}
	}
	assert(valid_move_cnt > 0);
	n->valid_move_cnt = valid_move_cnt;
	return n;
}
void mctsCreate(int id)
{
	mcts.root = createNode(id);
}
float mctsScore(int child_score, int child_sims, int sims)
{
	return (float)child_score / child_sims + sqrt(2*log(sims) / child_sims);
}
static void release(struct node* n)
{
	int i;
	if(n == NULL) return;
	for(i=0;i<n->moved_cnt;i++){
		unsigned char point = n->moveds[i];
		release(n->p_nmn[point>>4][point&0xF]);
	}
	free(n);
}
struct node* mctsMoveChildNode(unsigned char point)
{
	struct node *root = mcts.root;
	mcts.root = mcts.root->p_nmn[point>>4][point&0xF];
	if(mcts.root == NULL){
//		MSG("EMPTY ROOT: move=%02x\n", point);
		mcts.root = growNode(root, point);
	}
	// TODO: release root and children's memory
	root->p_nmn[point>>4][point&0xF] = NULL;
	release(root);
	return mcts.root;
}
int getRandomRes(struct node *node)
{
	struct node *n = (struct node *)calloc(1, sizeof(struct node));
	struct node *head = n;
	static unsigned char rand_node_move[81];
	*n = *node;
	while(1){
		int i;
		if(n->win_state == node->id){ release(head); return SC_WIN;
		}else if(n->win_state == OP_ID(node->id)){ release(head); return -SC_WIN;
		}else if(n->win_state != UNKNOWN){ release(head); return SC_ZERO; }
		unsigned char rand_move = n->valid_moves[rand() % n->valid_move_cnt];
		unsigned char y = rand_move >> 4, x = rand_move & 0xF;
		n->p_nmn[y][x] = growNode(n, rand_move);
		n->moveds[n->moved_cnt++] = rand_move;
		n = n->p_nmn[y][x];
	}
}
void mctsSimulation(void)
{
	static struct node *node_list[81];
	static unsigned char rand_node_move[81];
	int i, move_cnt = 0, node_cnt = 0;
	struct node *n = mcts.root;
	// select
	while(1){
		assert(n != NULL);
		node_list[node_cnt++] = n;
		if(n->valid_move_cnt != n->moved_cnt || n->win_state != UNKNOWN){ break; }
		n = n->child_best;
	}
	// expand & rollouts
#if 0
	if(n->win_state == UNKNOWN){
		move_cnt = 0;
		for(i=0;i<n->valid_move_cnt;i++){
			int y = n->valid_moves[i] >> 4, x = n->valid_moves[i] & 0xF;
			if(n->p_nmn[y][x] == NULL){
				rand_node_move[move_cnt++] = n->valid_moves[i];
			}
		}
		unsigned char rand_move = rand_node_move[rand() % move_cnt];
		unsigned char y = rand_move >> 4, x = rand_move & 0xF;
		n->p_nmn[y][x] = growNode(n, rand_move);
		n->moveds[n->moved_cnt++] = rand_move;
		n = n->p_nmn[y][x];
		n->sim_score = getRandomRes(n);
		node_list[node_cnt++] = n;
	}
#else
	while(n->win_state == UNKNOWN){
		move_cnt = 0;
		for(i=0;i<n->valid_move_cnt;i++){
			int y = n->valid_moves[i] >> 4, x = n->valid_moves[i] & 0xF;
			if(n->p_nmn[y][x] == NULL){
				rand_node_move[move_cnt++] = n->valid_moves[i];
			}
		}
		unsigned char rand_move = rand_node_move[rand() % move_cnt];
		unsigned char y = rand_move >> 4, x = rand_move & 0xF;
		n->p_nmn[y][x] = growNode(n, rand_move);
		n->moveds[n->moved_cnt++] = rand_move;
		n = n->p_nmn[y][x];
		node_list[node_cnt++] = n;
	}
#endif
	// backward propagation
	while(--node_cnt > 0){
		struct node *n_me     = node_list[node_cnt];
		struct node *n_parent = node_list[node_cnt-1];
		n_parent->simulations += 1;
		if(n_parent->id == n->id){
			n_parent->sim_score += n->sim_score;
		}else{
			n_parent->sim_score -= n->sim_score;
		}
		n_me->mcts_score = mctsScore(n_me->sim_score, n_me->simulations, n_parent->simulations);
		// TODO: update best child
		if(n_parent->child_max_score < n_me->mcts_score || ((rand()&1) && n_parent->child_max_score == n_me->mcts_score)){
			n_parent->child_max_score = n_me->mcts_score;
			n_parent->child_best = n_me;
		}else if(n_parent->child_best == n_me){
			int i;
			n_parent->child_max_score = -1;
			for(i=0;i<n_parent->moved_cnt;i++){
				unsigned char moveds = n_parent->moveds[i];
				if(n_parent->p_nmn[moveds>>4][moveds&0xF]->mcts_score > n_parent->child_max_score){
					n_parent->child_max_score = n_parent->p_nmn[moveds>>4][moveds&0xF]->mcts_score;
					n_parent->child_best = n_parent->p_nmn[moveds>>4][moveds&0xF];
				}
			}
		}
		assert(n_me->mcts_score >= 0);
		assert(n_parent && n_parent->child_best != NULL);
	}
}
int get_res(void){
	int i = 0;
	TEST_VALUE = 0;
	while(clock() - TIME_START < DEFAULT_TIME_PER_MOVE){
		mctsSimulation();
		TEST_VALUE++;
	}
	MSG("node visited: %d, sim:%d\n", TEST_VALUE, mcts.root->simulations);
	float select_mark = -1;
	int select_move = 0;
	for(i=0;i<mcts.root->moved_cnt;i++){
		int y = mcts.root->moveds[i] >> 4;
		int x = mcts.root->moveds[i] & 0xF;
		struct node *n = mcts.root->p_nmn[y][x];
		if(select_mark < (float)n->sim_score / n->simulations){
			select_mark = (float)n->sim_score / n->simulations;
			select_move = mcts.root->moveds[i];
		}
	}
	mcts.x = select_move & 0xF;
	mcts.y = select_move >> 4;
}

void round_init0(void){
	static int validActionCount, row, col, y, x;
	TIME_START = clock();
    scanf("%d%d", &y, &x);
    scanf("%d", &validActionCount);
    for (int i = 0; i < validActionCount; i++) { scanf("%d%d", &row, &col); }
	mctsCreate(y>=0?ID0:ID1);
	MSG("MY_FIRST?:%s\n", y<0?"YES":"NO");
	if(y>=0){
		mctsMoveChildNode((y<<4)|x);
		get_res();
	}else{
		mcts.x = 4; mcts.y = 4;
	}
}
void round_init(void){
	static int validActionCount, row, col, y, x;
    scanf("%d%d", &y, &x);
    scanf("%d", &validActionCount);
    for (int i = 0; i < validActionCount; i++) { scanf("%d%d", &row, &col); }
	mctsMoveChildNode((y<<4)|x);
}
int main(){
	init_maps();
#if 1
    round_init0();
    while (1) {
		TIME_START = clock();
		printf("%d %d\n", mcts.y, mcts.x);
		mctsMoveChildNode((mcts.y<<4)|mcts.x);
		round_init();
		get_res();
    }
#else
	mctsCreate(ID1);
	mctsMoveChildNode((4<<4)|4);
	while(GET_STATE(mcts.root->field, FIELD_ALL) == UNKNOWN){
		TIME_START = clock();
		get_res();
		printf("mctsMoveChildNode(%d);\n", (mcts.y<<4)|mcts.x);
//		dumpNode(mcts.root);
		mctsMoveChildNode((mcts.y<<4)|mcts.x);
	}
	release(mcts.root);
#endif
}

